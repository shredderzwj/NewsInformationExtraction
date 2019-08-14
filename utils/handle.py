# -*- coding: utf-8 -*-


import jieba
import re

from utils.langconv.langconv import Converter


def get_words(text):
	"""jieba 分词"""
	words = []
	text_filter = re.findall(r'[\u4e00-\u9fa5]+', text)    # 过滤掉非中文字符
	for x in text_filter:
		words += jieba.lcut(x)
	return words


def cht_to_chs(line):
	"""转换繁体到简体"""
	line = Converter('zh-hans').convert(line)
	line.encode('utf-8')
	return line


def chs_to_cht(line):
	"""转换简体到繁体"""
	line = Converter('zh-hant').convert(line)
	line.encode('utf-8')
	return line
