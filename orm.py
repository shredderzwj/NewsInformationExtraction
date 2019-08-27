# -*- coding: utf-8 -*-
# 使用 ORM 操作数据库

from sqlalchemy import Column, String, text, Integer

from conf import DataBase


class ExpressionWords(DataBase.Base):
    __tablename__ = 'expression_words'
    word = Column(String(20), primary_key=True)

    def to_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class ExpressionWordsOperate(DataBase):
    """获取 N 个词"""

    def __len__(self):
        count = self.session.query(ExpressionWords).count()
        return count

    def __call__(self, number=None):
        if number is None:
            query = self.session.query(ExpressionWords)
        else:
            query = self.session.query(ExpressionWords).limit(number)
        return self.__get_data(query)

    def __getitem__(self, item):
        query = self.session.query(ExpressionWords)[item]
        return self.__get_data(query)

    def __iter__(self):
        for x in self.session.query(ExpressionWords):
            yield x.word

    def __get_data(self, query):
        infos = []
        for x in query:
            infos.append(x.word)
        return infos

    def is_word_exists(self, word):
        """判断词是否存在数据库中"""
        query = self.session.query(ExpressionWords).filter(ExpressionWords.word == word)
        return self.session.query(
            query.exists()
        ).scalar()

    def add_word(self, word):
        """
        添加一个词
        :param word: str 词
        :return: 添加成功返回 True， 否则返回 None，一般是由于词库中已有此词
        """
        if not self.is_word_exists(word):
            self.session.add(ExpressionWords(word=word))
            self.session.commit()
            return True
        else:
            return None

    def add_words(self, words):
        """
        添加词，一次性添加多个
        :param words: list or tuple or set 词列表
        :return: 添加是否成功的 Bool 值 列表。若输入的不是列表、元祖、集合，则不进行操作，返回 None
        """
        if isinstance(words, (list, tuple, set)):
            opera_bools = []
            for word in words:
                if not self.is_word_exists(word):
                    self.session.add(ExpressionWords(word=word))
                    opera_bools.append(True)
                else:
                    opera_bools.append(None)
            self.session.commit()
            return opera_bools
        else:
            return None

    def del_word(self, word):
        """
        删除一个词
        :param word: str 要删除的词
        :return: 删除成功返回 True。否则返回 None， 一般是由于数据库中不存在此词。
        """
        if self.is_word_exists(word):
            self.session.query(ExpressionWords).filter(ExpressionWords.word == word).delete()
            self.session.commit()
            return True
        else:
            return None

