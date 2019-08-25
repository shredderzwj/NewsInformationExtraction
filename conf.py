# -*- coding: utf-8 -*-
# 项目配置文件


import os
import sys
import json
from sqlalchemy import Column, String, text, Integer
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class ModelPath(object):
    word2vec = ''    # 词向量模型
    expression_words_path = os.path.join(os.path.dirname(__file__), 'data', 'expression_words.json')
    ltp = r'D:\NLPdata\ltp_data_v3.4.0'         # ltp 模型存放文件夹路径
    ltp_cws = os.path.join(ltp, 'cws.model')
    ltp_ner = os.path.join(ltp, 'ner.model')
    ltp_parser = os.path.join(ltp, 'parser.model')
    if 'win' in sys.platform:
        ltp_pisrl = os.path.join(ltp, 'pisrl_win.model')
    elif 'linux' in sys.platform:
        ltp_pisrl = os.path.join(ltp, 'pisrl.model')
    ltp_pos = os.path.join(ltp, 'pos.model')


class DataBase(object):
    """设置数据库参数"""
    db_driver = "mysql+pymysql"  # 设置数据库软件[驱动]
    db_host = 'rm-8vbwj6507z6465505ro.mysql.zhangbei.rds.aliyuncs.com'  # 数据库地址
    db_user = 'root'  # 数据库用户名
    db_pwd = 'AI@2019@ai'  # 数据库密码
    db_db = 'alpha_zero'
    engine = create_engine('%s://%s:%s@%s/%s' % (db_driver, db_user, db_pwd, db_host, db_db))
    Session = sessionmaker(engine)
    session = Session()
    Base = declarative_base()


# class ExpressionWords(DataBase.Base):
#     __tablename__ = 'expression_words'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     word = Column(String(20))
#     count = Column(Integer, index=True)
#
#     def to_dict(self):
#         return {x.name: getattr(self, x.name) for x in self.__table__.columns}
#
#
# class ExpressionWordsGotor(DataBase):
#     """获取频率最高的前 N 个词"""
#
#     def __len__(self):
#         count = self.session.query(ExpressionWords).count()
#         return count
#
#     def __call__(self, number):
#         query = self.session.query(ExpressionWords).order_by(text('-count')).limit(number)
#         return self.get_data(query)
#
#     def get_data(self, query):
#         infos = []
#         for x in query:
#             infos.append(x.name)
#         return infos


class ExpressionWordsGotor(ModelPath):
    """获取频率最高的前 N 个词"""
    def __init__(self):
        fp = open(self.expression_words_path)
        self.expression_words = json.load(fp)
        self.len = len(self.expression_words)
        fp.close()

    def __len__(self):
        return self.len

    def __call__(self, number):
        if number >= self.len:
            return self.expression_words
        else:
            return self.expression_words[:number]

