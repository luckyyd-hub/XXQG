#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: model.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-08-01(星期四) 17:24
@Copyright © 2019. All rights reserved.
'''
import os
import re
import json
from sqlalchemy import Column,Integer, String, Text, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from lxml import etree
from . import logger


# 创建对象的基类:
Base = declarative_base()

# 定义Bank对象:
class Bank(Base):
    # 表的名字:
    __tablename__ = 'Bank'

    '''表的结构:
        id | catagory | content | options[item0, item1, item2, item3] | answer | note | bounds
        序号 | 题型 | 题干 | 选项 | 答案 | 注释 | 位置(保存时丢弃)
    '''
    id = Column(Integer,primary_key=True)
    catagory = Column(String(128), default='radio') # radio check blank challenge
    content = Column(Text, default='content')
    # options的处理，每个item用空格分隔开，若item本身包含空格，则replace为顿号(、)
    options = Column(Text, default='')
    answer = Column(String(256), nullable=True, default='')
    note = Column(Text, nullable=True, default='')
    bounds = Column(String(128), nullable=True, default='')

    def __init__(self, catagory, content, options, answer, note, bounds):
        self.catagory = catagory or 'radio' # 挑战答题-挑战题, 每日答题-单选题、多选题、填空题
        self.content = content or 'default content'
        self.options = options or ''
        self.answer = answer.upper() or ''
        self.note = note or ''
        self.bounds = bounds or ''

    def __repr__(self):
        return f'<Bank {self.content}>'

    def __str__(self):
        maxlen = 42
        if len(self.content) > maxlen:
            content = f'{self.content[:maxlen]}...'
        else:
            content = self.content
        content = re.sub(r'\s', '_', content)
        options = ''
        if self.options:
            options = f'O: {self.options}\n'
        return f'I: {self.id} {self.catagory}\nQ: {content:<50}\n{options}A: {self.answer}\n'

    def __eq__(self, other):
        return self.content == other.content
    
    @classmethod
    def from_challenge(cls, content, options='', answer='', note='', bounds=''):
        return cls(catagory='挑战题', content=content, options=options, answer=answer, note=note, bounds=bounds)

    @classmethod
    def from_daily(cls, catagory, content, options, answer, note):
        return cls(catagory=catagory, content=content, options=options, answer=answer, note=note, bounds='')

    def to_array(self):
        options = self.options.split(' ')
        array_bank = [self.id, self.answer, self.content]
        array_bank.extend(options)
        # array_bank.append(self.note)
        return array_bank

    def to_dict(self):
        json_bank = {
            "id": self.id,
            "catagory": self.catagory,
            "content": self.content,
            "options": self.options,
            "answer": self.answer,
            "note": self.note
        }
        return json_bank

    @classmethod
    def from_dict(cls, data):
        return cls(data['catagory'], data['content'], data['options'], data['answer'], data['note'], '')



class Model():
    def __init__(self, database_uri):
        # 初始化数据库连接:
        engine = create_engine(database_uri)
        # 创建DBSession类型:
        Session = sessionmaker(bind=engine)

        Base.metadata.create_all(engine)
        self.session = Session()

    def query(self, id=None, content=None, catagory='挑战题 单选题 多选题 填空题'):
        '''数据库检索记录'''
        catagory = catagory.split(' ')
        if id and isinstance(id, int):
            return self.session.query(Bank).filter_by(id=id).first()
        if content and isinstance(content, str):
            return self.session.query(Bank).filter(Bank.catagory.in_(catagory)).filter_by(content=content).first()
        return self.session.query(Bank).filter(Bank.catagory.in_(catagory)).all()

    def add(self, item):
        '''数据库添加纪录'''
        result = self.query(content=item.content, catagory=item.catagory)
        if result:
            logger.info(f'数据库已存在此纪录，无需添加纪录！')
        else:
            self.session.add(item)
            self.session.commit()
            logger.info(f'数据库添加记录成功！')

    # def delete(self, item):
    #     '''数据库删除记录'''
    #     to_del = self.qeury(content=item.content)
    #     if to_del:
    #         session.delete(to_del)
    #         session.commit()
    #     else:
    #         logger.info('数据库无此纪录!')

    # def temp_del(self, id):
    #     to_del = self.query(id=id)
    #     self.session.delete(to_del)
    #     self.session.commit()

    # def update(self, id, answer):
    #     '''数据库更新记录'''
    #     to_update = self.query(id=id)
    #     if to_update:
    #         to_update.answer = answer
    #         session.commit()
    #         logger.info(f'更新题目[{id}]的答案为“{answer}”')
    #     else:
    #         logger.info('数据库无此纪录!')

    def _to_json(self, filename, catagory='挑战题 单选题 多选题 填空题'):
        datas = self.query(catagory)
        # logger.debug(len(datas))
        output = [data.to_dict() for data in datas]
        with open(filename,'w',encoding='utf-8') as fp:
            json.dump(output,fp,indent=4,ensure_ascii=False)
        logger.info(f'JSON数据{len(datas)}条成功导出{filename}')
        return True




    def _from_json(self, filename, catagory='挑战题 单选题 多选题 填空题'):
        if(os.path.exists(filename)):        
            with open(filename,'r',encoding='utf-8') as fp:
                res = json.load(fp)
            for r in res:
                bank = Bank.from_dict(r)
                if '填空题' == bank.catagory:
                    if str(len(bank.answer.split(' '))) != bank.options:
                        continue
                self.add(bank)
            logger.info(f'JSON数据成功导入{filename}')
            return True
        else:
            logger.debug(f'JSON数据{filename}不存在')
            return False
    
    def _to_md(self, filename, catagory='挑战题 单选题 多选题 填空题'):
        pass

    def _to_xls(self, filename, catagory='挑战题 单选题 多选题 填空题'):
        from .common import xlser
        data = self.query(catagory=catagory)
        xs = xlser.Xlser(filename)
        xs.save(data)

    def upload(self, filename, catagory='挑战题 单选题 多选题 填空题'):
        filepath,fullflname = os.path.split(filename)
        fname,ext = os.path.splitext(fullflname)
        if '.json' == ext:
            self._from_json(filename, catagory)
        elif '.xls' == ext or '.xlsx' == ext:
            pass
        else:
            logger.info(f'不被支持的文件类型: {ext}')

    
    def download(self, filename, catagory='挑战题 单选题 多选题 填空题'):
        filepath,fullflname = os.path.split(filename)
        fname,ext = os.path.splitext(fullflname)
        if '.json' == ext:
            self._to_json(filename, catagory)
        elif '.xls' == ext or '.xlsx' == ext:
            self._to_xls(filename, catagory)
        elif '.md' == ext:
            self._to_md(filename, catagory)
        else:
            logger.info(f'不被支持的文件类型: {ext}')



if __name__ == "__main__":
    from argparse import ArgumentParser
    from . import logger
    logger.debug('running __main__')


    parse = ArgumentParser()
    parse.add_argument(dest='filename', metavar='filename', nargs="?", type=str, help='目标文件路径')
    parse.add_argument('-b', '--behavior', metavar='behavior', type=str, default='download', help='数据库操作，upload、download')
    parse.add_argument('-c', '--catagory', metavar='catagory', type=str, default='挑战题 单选题 多选题 填空题', help='题型：挑战题、单选题、多选题、填空题')
    parse.add_argument('-d', '--display', metavar='display', nargs='?', const=True, type=bool, default=False, help='打印')
    args = parse.parse_args()

    db = Model('sqlite:///./xuexi/src/database/data-dev.sqlite')
    if args.filename:
        if 'download' == args.behavior:
            db.download(args.filename, args.catagory)
        elif 'upload' == args.behavior:
            db.upload(args.filename, args.catagory)
        else:
            pass
    else:
        if args.display:
            data = db.query(catagory=args.catagory)
            for d in data:
                print(d)
            print(f'总数 {len(data)}题')
        else:
            print('''使用说明：
    python -m xuexi.model filename -b [upload|download] -c [挑战题|填空题|单选题|多选题]
    eg. 
        python -m xuexi.model ./xuexi/src/json/daily.json -b upload
        python -m xuexi.model ./xuexi/output.json
''')
            data = db.query()
            print(f'总数 {len(data)}题')
            for catagory in ['挑战题', '填空题', '单选题', '多选题']:
                data = db.query(catagory=catagory)
                print(f'{catagory} {len(data)}题')


