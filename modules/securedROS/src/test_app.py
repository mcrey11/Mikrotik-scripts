#!/usr/bin/env python
# coding: utf-8
import unittest
import sys
import secureROS

class TestStringMethods(unittest.TestCase):

    #def test_noRouter(self):
    #    router = secureROS.getRouter(-1);
    #    self.assertTrue ( router==None )

    def test_Router0_RO_connect(self): #no router cert check
        router = secureROS.getRouter(0,True);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_Router0_RW_connect(self): #no router cert check
        router = secureROS.getRouter(0,False);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_Router1_RO_connect(self): #router cert check
        router = secureROS.getRouter(1,True);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_Router1_RW_connect(self): #router cert check
        router = secureROS.getRouter(1,False);
        self.assertTrue ( router!=None )
        router.disconnect()

if __name__ == '__main__':
    unittest.main()
