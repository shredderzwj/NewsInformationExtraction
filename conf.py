# -*- coding: utf-8 -*-
# 项目配置文件


import os
import sys
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class ModelPath(object):
    word2vec = ''    # 词向量模型
    expression_words_path = os.path.join(os.path.dirname(__file__), 'data', 'expression_words.json')
    ltp = r'D:\NLPdata\ltp_data_v3.4.0'         # ltp 模型存放文件夹路径
    if not os.path.exists(ltp):
        ltp = '/home/student/project/project-01/ltp_data'
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
    # #################################### 服务器 ############################
    # db_driver = "mysql+pymysql"  # 设置数据库软件[驱动]
    # db_host = 'rm-8vbwj6507z6465505ro.mysql.zhangbei.rds.aliyuncs.com'  # 数据库地址
    # db_user = 'root'  # 数据库用户名
    # db_pwd = 'AI@2019@ai'  # 数据库密码
    # db_db = 'alpha_zero'
    # engine = create_engine('%s://%s:%s@%s/%s' % (db_driver, db_user, db_pwd, db_host, db_db))
    # ########################################################################

    # #################################### 本地 sqlite########################
    db_driver = "sqlite"  # 设置数据库软件[驱动]
    db_host = ''  # 数据库地址
    db_user = ''  # 数据库用户名
    db_pwd = ''  # 数据库密码
    db_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'alpha_zero.sqlite')
    engine = create_engine('%s://%s:%s@%s/%s?check_same_thread=False' % (db_driver, db_user, db_pwd, db_host, db_db))
    # ########################################################################

    Session = sessionmaker(engine)
    session = Session()
    Base = declarative_base()


