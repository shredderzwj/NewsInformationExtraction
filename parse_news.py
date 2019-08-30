# -*- coding: utf-8 -*-


from pyltp import SentenceSplitter, Segmentor, Postagger
from pyltp import NamedEntityRecognizer, Parser, SementicRoleLabeller
from collections import defaultdict

from conf import ModelPath
from utils.handle import TextHandle


class SentenceParse(ModelPath):
    def __init__(self):
        # 分词
        self.segmentor = Segmentor()
        self.segmentor.load(self.ltp_cws)

        # 词性标注
        self.postagger = Postagger()
        self.postagger.load(self.ltp_pos)

        # 命名实体识别
        self.recognizer = NamedEntityRecognizer()
        self.recognizer.load(self.ltp_ner)

        # 依存句法分析
        self.parser = Parser()
        self.parser.load(self.ltp_parser)

        # 语义角色标注
        self.labeller = SementicRoleLabeller()
        self.labeller.load(self.ltp_pisrl)

    def __call__(self, sentence, *args, **kwargs):
        words = self.get_words(sentence)
        postags = self.get_postagger(words)
        ner = self.get_recognizer(words, postags)
        arcs = self.get_parse(words, postags)
        # roles = self.get_rolelabel(words, postags, arcs)
        parse_result = {
            "sentence": sentence,
            "words": words,
            "postags": postags,
            "ner": ner,
            "arcs": [(arc.head, arc.relation) for arc in arcs],
            # "roles": [
            #     [role.index, [[arg.name, (arg.range.start, arg.range.end)] for arg in role.arguments]] for role in roles
            # ],
        }
        # print("*"*80)
        # for k, v in parse_result.items():
        #     print(k, v)
        return parse_result
    # , [arg.name, [arg.range.start, arg.range.end]]
    # for arg in role.arguments]
    def get_sentences(self, news):
        """
        分句
        :param news: str 新闻文本
        :return:  list 句子列表
        """
        return list(SentenceSplitter.split(news))

    def get_words(self, sentence):
        """
        分词
        :param sentence: str 句子
        :return: list 分词列表
        """
        return list(self.segmentor.segment(sentence))

    def get_postagger(self, words):
        """
        词性标注
        :param words:
        :return: list 词性
        """
        return list(self.postagger.postag(words))

    def get_recognizer(self, words, postags):
        """
        命名实体识别
        :param words: list 词列表
        :param postags: list 词性列表
        :return: list 命名实体列表
        """
        return list(self.recognizer.recognize(words, postags))

    def get_parse(self, words, postags):
        """
        依存句法分析
        :param words: list 词列表
        :param postags: list 词性列表
        :return: 依存关系
        """
        arcs = self.parser.parse(words, postags)
        return arcs

    def get_rolelabel(self, words, postags, arcs):
        """
        语义角色标注
        :param words: list 词列表
        :param postags: list 词性列表
        :param arcs: 依存句法分析结果
        :return: 语义角色标注
        """
        roles = self.labeller.label(words, postags, arcs)
        return roles

    def release(self):
        """释放模型"""
        self.segmentor.release()
        self.recognizer.release()
        self.parser.release()
        self.postagger.release()
        self.labeller.release()


class Parse(object):
    # 解析 谁 说了什么
    sen_parse = SentenceParse()

    # 设置启动程序时加载 激活 词列表
    # from orm import ExpressionWordsOperate
    # active_words = ExpressionWordsOperate()[:]

    def __init__(self, news, active_words):
        """
        :param news: str 新闻文本
        :param active_words: list 表示“说”的词列表
        """
        self.news = news
        self.active_words = active_words

    def __call__(self):
        self.sentences = self.__handel(self.news)
        # for x in self.sentences:
        #     print(x)
        self.sentences_goal, self.parse, self.expression_words = self.__get_expression_sentences(self.sentences)
        # print("*"*80)
        # for x in self.sentences_goal:
        #     print(x)

        self.ners = self.get_named_entity(self.parse, self.expression_words)
        # print(self.ners)
        self.contents = self.get_content(self.ners, self.parse, self.sentences)
        infos = [
            [
                self.ners[i]['sbv'][1],
                self.ners[i]['hed'][1],
                self.contents[i],
            ] for i in self.contents.keys()
        ]
        if infos:
            return infos
        else:
            return self.news

    def __handel(self, news):
        news = TextHandle.cht_to_chs(news)
        sentences = []
        for line in news.strip().split('\n'):
            sentences += list(SentenceSplitter.split(line.strip()))
            # sentences += [line.strip()]
        return sentences

    ## changed ##
    def __get_expression_sentences(self, sentences):
        """ 检测句子是否含有 说 的意思 """
        # 去重
        sentences = list(set(sentences))
        
        # 通过求交集的方式找与“说”意思相近的单词
        parse = {}
        expression_words = defaultdict(list)
        sentences_goal = {}
        for i, sen in enumerate(sentences):
            # print(i, sen)
            sentences_goal[i] = sen
            parse[i] = sen_parse(sen)
            words = parse[i]["words"]
            overlap = [val for val in list(words) if val in expression_words_all]
            if overlap != []:
                expression_words[i] = overlap
        return sentences_goal, parse, expression_words

    ## changes ##
    def get_named_entity(self, parse, expression_words):
        """获取 命名主体"""
        ners = defaultdict(dict)
        for i in parse.keys():
            postags = parse[i]['postags']
            ner = parse[i]['ner']
            words = parse[i]['words']
            arcs = parse[i]['arcs']
            expression_word_list = expression_words[i]

            for expression_word in expression_word_list:

                if expression_word not in words:
                    continue

                expression_word_index = words.index(expression_word)

                if 'v' not in list(postags[expression_word_index]):
                    continue

                # 如果“说”的同义词不是句子的核心，那么句子的核心与其是并列关系呢（COO）？
                # 与句子的核心HED有COO关系的词
                if 0 in arcs[expression_word_index] or 0 in arcs[arcs[expression_word_index][0] - 1]:
                    for j, (k, v) in enumerate(arcs):
                        
                        postags_list = ['j', 'n', 'nh', 'ni', 'ns', 'nz']
                        # postags_list = ['j', 'k', 'm', 'nd', 'nl', 'nt', 'n', 'nh', 'ni', 'ns', 'nz']
                        # 根据依存句法分析、命名实体识别、和词性标注。下面 if 语句解释为：
                        # （找到主谓关系 and 主语要与谓语关联） and（主语要识别为命名实体or 是一些词性可以表示实体的名词）
                        
                        if (v == 'SBV' and (k == expression_word_index + 1 or k == arcs[expression_word_index][0])) and (set(list(ner[j])) & {"S", "B", "I", "E"} or postags[j] in postags_list):
                            sbv_start = j
                            # 获取修饰词
                            # for m in range(5):
                            for m in range(5):  
                                if j - 1 - m >= 0:
                                    if arcs[j - 1 - m][1] == 'ATT':  # and arcs[j - 1 - m][0] - 1 == j:
                                        sbv_start = j - 1 - m
                            ners[i] = {
                                'hed': (expression_word_index, expression_word),
                                'sbv': ((sbv_start, j), ''.join(words[sbv_start:j+1])),
                            }
                else:
                    continue
        return ners

    def get_content(self, ners, parse, sentence):
        """获取 说 的内容"""
        contents = defaultdict(str)
        for i in ners.keys():
            words = parse[i]['words']
            hed_index = ners[i]['hed'][0]
            sbv_index = ners[i]['sbv'][0]
            content_front_str = ''
            content_back_str = ''
            try:
                hed_index_next = hed_index + 1
                # 获取引号中的内容, 并且引号 距 “说” 不能太远
                if set(words) & {'"', "'", "“", "‘"} and abs(words.index((set(words) & {'"', "'", "“", "‘"}).pop()) - hed_index) <= 3:
                    contents[i] = words[words.index((set(words) & {'"', "'", "“", "‘"}).pop()):]
                    if not set(words) & {'"', "'", "’", "”"}:
                        for j in range(5):
                            content_back_str += sentence[i + 1 + j]
                            if set(sentence[i + 1 + j]) & {'"', "'", "’", "”"}:
                                break

                # 表示说的词在句尾，说的内容可能在前面，则获取前面的内容
                elif words[hed_index_next] in ['。', "！", "？", "!", "?", "…", ".", "……"]:
                    if set(sentence[i - 1]) & {'"', "'", "’", "”"}:
                        for j in range(5):
                            content_front_str = sentence[i - 1 - j] + content_front_str
                            if set(sentence[i - 1 - j]) & {'"', "'", "“", "‘"}:
                                break
                    # content_front_str += sentence[i - 1]
                    contents[i] = words[:sbv_index[0]]

                # 没有引号的，获取表示说的词后面的内容。
                elif words[hed_index_next] in [":", "：", ',', '，']:
                    contents[i] = words[hed_index_next + 1:]
                else:
                    contents[i] = words[hed_index_next:]
            except IndexError:
                content_front_str += sentence[i - 1]
                contents[i] = words[:sbv_index]
            contents[i] = content_front_str + "".join(contents[i]) + content_back_str
        return contents


if __name__ == '__main__':
    npa = Parse('香料店老板说今年的生意不太好')
    print(npa())

