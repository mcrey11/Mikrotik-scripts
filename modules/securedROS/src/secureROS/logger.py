import logging, logging.handlers
import functools
import settings

class _DummyLogger():
    def __init__(self, fdebug=False):
        self._debug=fdebug

    def debug(self,msg):
        if self._debug:
            print("DEBUG: {}".format(msg))

    def error(self,msg):
        if self._debug:
            print("ERROR: {}".format(msg))

    def warning(self,msg):
        if self._debug:
            print("WARNING: {}".format(msg))

logger = _DummyLogger(True); 

debug = False
logger_handlers = []

def getLoggerName():
    return "securerosapi"

def log(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        logger = logging.getLogger(getLoggerName())
        logger.debug('>>> Entering: %s', func.__name__)
        result = func(*args, **kwargs)
        logger.debug('<<< Exiting: {}, res={}'.format(func.__name__,result))
        return result
    return decorator

def initLogger(fdebug=False):
        global logger
        global logger_handlers
        global debug

        #if logger!=None:
        #    return
        debug=False
        if hasattr(settings,"debug"):
            debug=fdebug or settings.debug
        try:
            logger_name=getLoggerName()
            log_file = "{0}/{1}.log".format(settings.app_log_dir, logger_name)
            logging.basicConfig(level=(logging.INFO,logging.DEBUG)[debug])
            logger = logging.getLogger(logger_name)
            # create file handler which logs even debug messages
            # fh = logging.FileHandler(log_file)
            #if not os.path.isfile(log_file):
            #    touch(log_file)
            fh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024, backupCount=5, encoding=None, delay=0)
            fh.setLevel((logging.INFO,logging.DEBUG)[debug])
            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)
            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            # add the handlers to the logger
            logger.addHandler(fh)
            logger.addHandler(ch)
            logger.debug("Initing logger...")
            logger_handlers = [fh.stream]
        except Exception as inst:
            logger.warning("Failed to create logger")
            logger.error(type(inst))
            logger.error(inst.args)
            logger.error(inst)
            raise
        return logger

initLogger()
