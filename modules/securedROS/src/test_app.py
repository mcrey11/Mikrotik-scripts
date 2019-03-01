#!/usr/bin/env python
# coding: utf-8
import unittest
import sys
import secureROS
import secureROS.logger

log    = secureROS.logger.log
logger = secureROS.logger.logger

getfname = lambda n=0: "Calling test: {}".format(sys._getframe(n + 1).f_code.co_name)

class TestStringMethods(unittest.TestCase):

    def test_textOnly(self):
        router = secureROS.getRouter(-1);
        self.assertTrue ( router==None )

if __name__ == '__main__':
    try:
        logger.debug("Starting unit tests...")
        unittest.main()
    except Exception as inst:
        logger.error(type(inst))
        logger.error(inst.args)
        logger.error(inst)
    else:
        logger.debug("Exiting script...")
    logger.debug("Script is off...")
