import os, sys
import logger
import ssl
import json
import rosapi
from collections import ChainMap
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

## helper
def cmd_not_impl(object,cmd,args=None):
    return "*{}* : `{}` not impelmented".format(object,cmd)


class RosAPIObject(object):

    def __init__(self, parent, attr_name):
        self.name   = attr_name
        self.parent = parent
        logger.debug("RosAPIObjects init {}->{} ".format(self.parent.name,self.name))

    def __str__(self):
        return "RosAPIObject, name={}->{}".format(self.parent.name,self.name)

    def __getattr__(self, name):
        if name.startswith("__"):
            #logger.debug("Attribute error: {}".format(name))
            raise AttributeError
        logger.debug("GETATTR name={} -> {}".format(self.name,name))
        return RosAPIObject(self,name)

    @log
    def __call__(self, *args, **kwargs):
        logger.debug("Call to {}({},{})".format(self.name,args,kwargs))
        #unwind objects and get str repr of command
        cmd=""
        obj=self
        while obj.name!="root":
            cmd="/"+obj.name+cmd
            obj=obj.parent
        return obj.do( cmd, *args, **kwargs )

class RouterContext(object):
    api  = None
    name = "root"
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

            #method = ( rosapi.login_plain, )


            kwargs={ "host" : cfg['ip'], 
                     "port" : cfg['port'],
                     #"login_methods" : method,
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
                api = rosapi.connect(**kwargs)
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

#    @log
#    @command("/")
#    def get_AddressListItems(self,cmd,args=None):
#        return cmd_not_impl(self,cmd,args)

    @log
    def console(self):
        print("Enter /quit to exit console mode!")
        while True:
            text=input("#>")
            if text=="/quit":
                break
            if self.api and text:
                try:
                    res=self.api(cmd=text)
                except Exception as inst:
                    print("ERROR: {}".format(str(inst)))
                else:
                    if res:
                        print(res)


    @log
    def get_AddressListItems(self,addresListName):
        if not self.api:
            return None
        try:
            params = {'?=list': addresListName}
            #res=self.api(cmd="/ip/firewall/address-list/print")
            res=self.api(cmd="/ip/firewall/address-list/print",**params)
        except Exception as inst:
            print("ERROR: {}".format(str(inst)))
        else:
            if res:
                    print(res)


    def __getattr__(self, name):
        if name.startswith("__"):
            #logger.debug("Attribute error: {}".format(name))
            raise AttributeError
        logger.debug("GETATTR {}->{}".format(self.name,name))
        r=RosAPIObject(self, name)
        return r

    @log
    def do(self, text, where=None, **kwargs):
        logger.debug("Execute:\n cmd={}\n kwargs={}".format(text,kwargs))
        res=None
        if not self.api:
           return res
        
        try:
            res=self.api(cmd=text, where=where, **kwargs)
        except Exception as inst:
            logger.error(str(inst))
        return res

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


