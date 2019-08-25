# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import pandas as pd
from collections import defaultdict


class DBConf(object):
    """设置数据库参数"""
    db_driver = "mysql+pymysql"   # 设置数据库软件[驱动]
    db_host = 'rm-8vbwj6507z6465505ro.mysql.zhangbei.rds.aliyuncs.com'    # 数据库地址
    db_user = 'root'              # 数据库用户名
    db_pwd = 'AI@2019@ai'         # 数据库密码
    db_db = 'stu_db'              # 数据库名
    db_table = 'news_chinese'     # 数据库表
    engine = create_engine('%s://%s:%s@%s/%s' % (db_driver, db_user, db_pwd, db_host, db_db))
    Session = sessionmaker(engine)
    session = Session()
    Base = declarative_base()


class News(DBConf.Base):
    """表结构"""
    __tablename__ = DBConf.db_table
    id = Column(Integer, primary_key=True)
    author = Column(String(32))
    source = Column(String(32))
    content = Column(Text)
    feature = Column(String(256))
    title = Column(String(32))
    url = Column(String(32))

    def to_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class Record(DBConf):
    """通过索引获取数据库中的记录，并转换为字典格式，如果是切片操作则返回一个生成器"""
    def __len__(self):
        count = self.session.query(News).count()
        return count

    def __getitem__(self, position):
        query = self.session.query(News)[position]
        if isinstance(query, (list, tuple)):
            return self.get_data(query)
        else:
            return query.to_dict()

    def get_data(self, query):
        for x in query:
            yield x.to_dict()


def test():
    r = Record()
    print("总共有 %d 条记录" % len(r))
    print("type(r[1]) ->", type(r[1]))
    print('type(r[:2]) ->', type(r[:5]))
    print('\n', "*"*30, 'r[10]', "*"*30)
    print(r[10])
    for i, x in enumerate(r[:5]):
        print('\n', "*"*30, 'r[%d]' % i, "*"*30)
        print(x)


def get_data_save_to_file(file_path):
    """file_path保存文件的路径，保存为csv文件，只保留 title 和 content 两个字段的数据"""
    if not os.path.exists(os.path.dirname(file_path)):
        print('保存的文件路径不存在！')
        return
    print('正在获取数据...')
    r = Record()
    data = defaultdict(list)
    for x in r[:]:
        for k, v in x.items():
            data[k].append(v)
    print('正在保存数据...')
    df = pd.DataFrame(data=data)
    df = df[
        ['title', 'content']
    ]
    df.to_csv(file_path)
    print('完成')


if __name__ == "__main__":
    test()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    name = 'news.csv'
    folder = 'data'
    path = os.path.join(root, folder, name)
    # get_data_save_to_file(path)
