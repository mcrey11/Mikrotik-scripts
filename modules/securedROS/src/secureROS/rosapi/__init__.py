# -*- coding: UTF-8 -*-
#1. Initially based on https://github.com/luqasz/librouteros
#2. ROS >= 6.43

from socket import create_connection, error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT
from collections import ChainMap

from .exceptions import TrapError, FatalError, ConnectionError, MultiTrapError
from .connections import ApiProtocol, SocketTransport
from .api import RosAPI


def login_plain(api, username, password):
    """Login using post routeros 6.43 authorization method."""
    api('/login', **{'name': username, 'password': password})

defaults = {
            'timeout': 10,
            'port': 8729, #ssl port by default
            'saddr': '',
            'subclass': RosAPI,
            'encoding': 'ASCII',
            'ssl_wrapper': lambda sock: sock,
            'login_methods': (login_plain,),
            }


def connect(host, username, password, **kwargs):
    """
    Connect and login to routeros device.
    Upon success return a Api class.

    :param host: Hostname to connecto to. May be ipv4,ipv6,FQDN.
    :param username: Username to login with.
    :param password: Password to login with. Only ASCII characters allowed.
    :param timeout: Socket timeout. Defaults to 10.
    :param port: Destination port to be used. Defaults to 8729.
    :param saddr: Source address to bind to.
    :param subclass: Subclass of Api class. Defaults to Api class from library.
    :param ssl_wrapper: Callable (e.g. ssl.SSLContext instance) to wrap socket with.
    :param login_methods: Tuple with callables to login methods to try in order.
    """
    arguments = ChainMap(kwargs, defaults)
    transport = create_transport(host, **arguments)
    protocol = ApiProtocol(transport=transport, encoding=arguments['encoding'])
    api = arguments['subclass'](protocol=protocol)

    for method in arguments['login_methods']:
        try:
            method(api=api, username=username, password=password)
            return api
        except (TrapError, MultiTrapError):
            pass
        except (ConnectionError, FatalError):
            transport.close()
            raise


def create_transport(host, **kwargs):
    try:
        sock = create_connection((host, kwargs['port']), kwargs['timeout'], (kwargs['saddr'], 0))
        sock = kwargs['ssl_wrapper'](sock)
        return SocketTransport(sock)
    except (SOCKET_ERROR, SOCKET_TIMEOUT) as error:
        raise ConnectionError(error)
    return SocketTransport(sock=sock)
