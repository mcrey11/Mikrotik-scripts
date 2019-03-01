try:
    import logger
    log    = logger.log
    logger = logger.logger
except Exception as inst:
    logger.warning("Failed to create logger")
    logger.error(type(inst))
    logger.error(inst.args)
    logger.error(inst)
    raise

class RouterContext:
    def __init__(self, *args, **kwds):
        pass

    @log
    def cmd_status(self,object,cmd,args=None):
        return cmd_not_impl(object,cmd,args)

@log
def getRouter(rid):
    return None