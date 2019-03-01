import os, sys
import logger
import ssl
import json
from librouteros import connect
from librouteros.login import login_plain, login_token

#try:
#    import logger
#except Exception as inst:
#    logger.warning("Failed to create logger")
#    logger.error(type(inst))
#    logger.error(inst.args)
#    logger.error(inst)
#    raise

log    = logger.log
logger = logger.logger

class RouterContext:
    api = None

    def __init__(self, rid, fReadOnly=True):
        dir_cur=os.path.dirname(os.path.realpath(__file__))
        config=self.read_config(dir_cur)

        sid=str(rid)
        cfg=config.get(sid,None)
        if cfg!=None:
            #ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False

            if cfg["api_ca_cert"]:
                cert=os.path.join(dir_cur, 'certs')
                cert=os.path.join(cert, cfg["api_ca_cert"] )
                ctx.load_verify_locations(cafile=cert)
            else:
                #### NO CERT
                #  In the case no certificate is used in '/ip service' settings then anonymous Diffie-Hellman cipher have to be used to establish connection. 
                ctx.verify_mode = ssl.CERT_NONE
                ctx.set_ciphers('ADH')

            method = (login_plain, )


            kwargs={ "host" : cfg['ip'], 
                     "port" : cfg['port'],
                     "login_methods" : method,
                     "ssl_wrapper" : ctx.wrap_socket 
                    }
            kwargs["username"] = cfg[ ('api_rw_user','api_ro_user')[fReadOnly] ]
            kwargs["password"] = cfg[ ('api_rw_pass','api_ro_pass')[fReadOnly] ]

            try:
                logger.debug("Trying connect to router with params:")
                for k,v in kwargs.items():
                    if k=="password":
                        v="*"*len(v)
                    logger.debug("  {}={}".format(k,v))
                api = connect(**kwargs)
            except Exception as inst:
                logger.error("Failed to connect to router!")
                logger.error(type(inst))
                logger.error(inst.args)
                logger.error(inst)
            else:
                logger.debug("Successfully connected to router!")
                self.api=api

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        if self.api!=None:
            logger.debug("Disconnecting from router...")
            self.api.close()
            self.api=None

    def read_config(self, path):
        #read config
        config=dict()
        try:
            logger.debug("Parsing config file (json)...")
            path=os.path.join(path,'routers.json')
            with open(path) as f:
                config = json.load(f)
        except Exception as inst:
            logger.error(type(inst))
            logger.error(inst.args)
            logger.error(inst)
            return None
        finally:
            logger.debug("JSON succesfully parsed.")
            for section,cfg in config.items():
                logger.debug("{} : {}".format(section,cfg))
            mod = sys.modules[self.__module__]
        return config

    @log
    def cmd_status(self,object,cmd,args=None):
        return cmd_not_impl(object,cmd,args)

@log
def getRouter(rid,readonly=True):
    try:
        context=RouterContext(rid,readonly)
    except Exception as inst:
        logger.error("Failed to connect to router!")
        logger.error(type(inst))
        logger.error(inst.args)
        logger.error(inst)
        return None
    return None if context.api==None else context