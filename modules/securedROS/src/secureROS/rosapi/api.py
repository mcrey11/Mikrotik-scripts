# -*- coding: UTF-8 -*-

from posixpath import join as pjoin
import pyparsing as pp

from .exceptions import TrapError, MultiTrapError
from logger import *


class Parser:

    api_mapping = {'yes': True, 'true': True, 'no': False, 'false': False}

    @staticmethod
    def apiCast(value):
        """
        Cast value from API to python.

        :returns: Python equivalent.
        """
        try:
            casted = int(value)
        except ValueError:
            casted = Parser.api_mapping.get(value, value)
        return casted

    @staticmethod
    def parseWord(word):
        """
        Split given attribute word to key, value pair.

        Values are casted to python equivalents.

        :param word: API word.
        :returns: Key, value pair.
        """
        _, key, value = word.split('=', 2)
        value = Parser.apiCast(value)
        return (key, value)


class Composer:

    python_mapping = {True: 'yes', False: 'no'}

    @staticmethod
    def pythonCast(value):
        """
        Cast value from python to API.

        :returns: Casted to API equivalent.
        """
        # this is necesary because 1 == True, 0 == False
        if type(value) == int:
            return str(value)
        else:
            return Composer.python_mapping.get(value, str(value))

    @staticmethod
    def composeWord(key, value):
        """
        Create a attribute word from key, value pair.
        Values are casted to api equivalents.
        """
        return '={}={}'.format(key, Composer.pythonCast(value))

    @staticmethod
    def composeWhere(s) -> list:
        def call_op_Unary(tokens):
            res=""
            op, v = tokens[0]
            if op=="HAS":
                res="?{}\n".format(v)
            elif op=="NOT":
                res="{}?#!\n".format(v)
            else:
                raise
            return res

        def call_op_Binary(tokens):
            res=""
            a,op,b=tokens[0][:3]
            if op=='==':
                res="?={}={}\n".format(a,b)
            elif op=="!=":
                res="?={}={}\n?#!\n".format(a,b)
            elif op=="<":
                res="?<{}={}\n".format(a,b)
            elif op==">":
                res="?>{}={}\n".format(a,b)
            elif op=="<=":
                res="?>{}={}\n?#!\n".format(a,b)
            elif op==">=":
                res="?<{}={}\n?#!\n".format(a,b)
            elif op=="AND" or op=="OR": #can be more than 3 tokens!
                if op=="AND": 
                    o="?#&\n"
                elif op=="OR": 
                    o="?#|\n"
                res="".join(tokens[0][0::2])+o*((len(tokens[0])-1)//2)
            else:
                raise

            return res

        def parseaction_identifier(str,location,tokens):
            m={ "true" : "yes",
                "yes"  : "yes", #not remove - adds ignore case to "yes" i.e. allows Yes, YES, yes etc 
                "false": "no" , 
                "no"   : "no"   #not remove - adds ignore case to "no" i.e. allows NO, no, No etc 
              }
            s=m.get( tokens[0].lower(), None)
            if s:
                return s
            return None

        number     = pp.Word(pp.nums)
        string     = pp.quotedString.setParseAction( pp.removeQuotes )
        identifier = pp.Word(pp.alphas+".", pp.alphanums + "-_").setParseAction(parseaction_identifier)
        
        operand = identifier | number | string

        operator        = pp.Regex(">=|<=|!=|>|<|==").setName("operator")
        
        expr = pp.operatorPrecedence(operand,[
                                            (pp.CaselessKeyword("HAS"), 1, pp.opAssoc.RIGHT, call_op_Unary),
                                            (operator,                  2, pp.opAssoc.LEFT,  call_op_Binary),
                                            (pp.CaselessKeyword("NOT"), 1, pp.opAssoc.RIGHT, call_op_Unary),
                                            (pp.CaselessKeyword("AND"), 2, pp.opAssoc.LEFT,  call_op_Binary),
                                            (pp.CaselessKeyword("OR"),  2, pp.opAssoc.LEFT,  call_op_Binary),
                                               ])

        try:
            res = expr.parseString( s, parseAll=True )
        except Exception as inst:
            logger.error("Failed to parse: {}\n{}".format(s, str(inst)))
            return None

        return res[0].split()

class RosAPI(Composer, Parser):

    def __init__(self, protocol):
        self.protocol = protocol

    def __call__(self, cmd, where=None, **kwargs):
        """
        Call Api with given command.

        :param cmd:    Command word. eg. /ip/address/print
        :param where:  "Where" clause in human readable form
        :param kwargs: Dictionary with optional arguments.
        """

        words = [ self.composeWord(key, value) for key, value in kwargs.items() ]
        if where:
            words=Composer.composeWhere(where)+words
        self.protocol.writeSentence(cmd, *words)
        return self._readResponse()

    def _readSentence(self):
        """
        Read one sentence and parse words.

        :returns: Reply word, dict with attribute words.
        """
        reply_word, words = self.protocol.readSentence()
        words = dict(self.parseWord(word) for word in words)
        return reply_word, words

    def _readResponse(self):
        """
        Read untill !done is received.

        :throws TrapError: If one !trap is received.
        :throws MultiTrapError: If > 1 !trap is received.
        :returns: Full response
        """
        response = []
        reply_word = None
        while reply_word != '!done':
            reply_word, words = self._readSentence()
            response.append((reply_word, words))

        self._trapCheck(response)
        # Remove empty sentences
        return tuple(words for reply_word, words in response if words)

    def close(self):
        self.protocol.close()

    @staticmethod
    def _trapCheck(response):
        traps = tuple(words for reply_word, words in response if reply_word == '!trap')
        if len(traps) > 1:
            traps = tuple(
                    TrapError(message=trap['message'], category=trap.get('category'))
                    for trap in traps
                    )
            raise MultiTrapError(*traps)
        elif len(traps) == 1:
            trap = traps[0]
            raise TrapError(message=trap['message'], category=trap.get('category'))

    @staticmethod
    def joinPath(*path):
        """
        Join two or more paths forming a command word.

        >>> api.joinPath('/ip', 'address', 'print')
        >>> '/ip/address/print'
        """
        return pjoin('/', *path).rstrip('/')
