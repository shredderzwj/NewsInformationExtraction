# -*- coding: utf-8 -*-
# 处理数据。繁简转换，分词等

import jieba
import re
import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
if current_path not in sys.path:
	sys.path.append(current_path)

from langconv.langconv import Converter


class TextHandle(object):
	def __call__(self, text, out_type='str', zh_type='zh_cn', *args, **kwargs):
		"""

		:param text:  str 需要分词的文本
		:param out:  str 选择输出的类型，
						'str' -> 以空格分隔的字符串
						otherwise -> 列表
		:param zh_type: 见 get_words 方法
		:param args:  jieba.lcut 的位置参数
		:param kwargs: 	jieba.lcut 的关键字参数
		:return: str or list 分词结果。
		"""
		words_list = self.get_words(text, zh_type, *args, **kwargs)
		if out_type == 'str':
			return self.words_list_to_str(words_list)
		return words_list

	@classmethod
	def get_words(cls, text, zh_type='zh_cn', *args, **kwargs):
		"""
		jieba 分词
		:param text:  str 需要分词的文本
		:param zh_type:  str， optional 繁简转换的选项。
						zh_cn 转换为简体（默认）
						zh_tw 转换为繁体
						otherwise 不进行转换
		:param args:  jieba.lcut 的位置参数
		:param kwargs: 	jieba.lcut 的关键字参数
		:return: list 分词结果
		"""
		words = []
		if zh_type == 'zh_cn':
			text = cls.cht_to_chs(text)
		elif zh_type == 'zh_tw':
			text = cls.chs_to_cht(text)
		text_filter = re.findall(r'[\u4e00-\u9fa5]+', text)    # 过滤掉非中文字符
		for x in text_filter:
			words += jieba.lcut(x, *args, **kwargs)
		return words

	@staticmethod
	def cht_to_chs(line):
		"""转换繁体到简体"""
		line = Converter('zh-hans').convert(line)
		line.encode('utf-8')
		return line

	@staticmethod
	def chs_to_cht(line):
		"""转换简体到繁体"""
		line = Converter('zh-hant').convert(line)
		line.encode('utf-8')
		return line

	@staticmethod
	def words_list_to_str(word_list):
		"""
		将分词列表转换为 以空格分隔的字符串
		:param word_list:  list 词列表
		:return: str 以空格分隔的词列表字符串
		"""
		temp = ' '.join(word_list)
		eof = ' '
		if not temp: eof = ''
		return ' '.join(word_list) + eof


if __name__ == '__main__':
	import pandas as pd
	in_file = r'D:\NLPdata\news.csv'
	out_file = r'D:\NLPdata\news.words'
	handle = TextHandle()
	df = pd.read_csv(in_file)
	with open(out_file, 'w', encoding='utf-8') as fp:
		for i, (index, row) in enumerate(df.iterrows()):
			title_split = handle(str(row.title))
			content_split = handle(str(row.content))
			fp.write(title_split + '\n' + content_split + '\n')
			print(i)
