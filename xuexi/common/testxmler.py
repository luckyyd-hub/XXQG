
import re
from pathlib import Path
from lxml import etree
from .. import logger

class Xmler(object):
    def __init__(self, path=Path('./xuexi/src/xml/reader.xml')):
        self.path = path
        self.root = None

    def load(self):
        self.root = etree.parse(str(self.path))

    def texts(self, rule:str)->list:
        '''return list<str>'''
        # logger.debug(f'xpath texts: {rule}')
        res = [x.replace(u'\xa0', u' ') for x in self.root.xpath(rule)]
        res = [' ' if '' == x else x for x in res]
        logger.debug(res)
        return res

    def pos(self, rule:str)->list:
        '''return list<complex>'''
        logger.debug(rule)
        res = self.texts(rule)
        logger.debug(res)
        points = [str2complex(x) for x in res]
        if len(points) == 1:
            res = points[0]
        else:
            res = points
        logger.debug(res)
        return res

    def content(self, rule:str)->str:
        '''return str'''
        logger.debug(rule)
        # res = self.texts(rule) # list<str>
        # res = ' '.join([" ".join(x.split()) for x in self.texts(rule)])
        res = ''.join(self.texts(rule))
        logger.debug(res)
        return res

    def options(self, rule:str)->str:
        res = [re.sub(r'\s+', '、', x) for x in self.root.xpath(rule)]
        logger.debug(res)
        res = ' '.join(res)
        logger.debug(res)
        return res

    def count(self, rule:str)->int:
        '''return int'''
        logger.debug(rule)
        res = self.root.xpath(rule)
        return len(res)

    # def element(self, rule:str)->object:
    #     res = self.root.xpath(rule)
    #     return res
