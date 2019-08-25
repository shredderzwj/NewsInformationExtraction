# -*- coding: utf-8 -*-


from pyltp import SentenceSplitter, Segmentor, Postagger
from pyltp import NamedEntityRecognizer, Parser, SementicRoleLabeller
from collections import defaultdict

from conf import ModelPath, ExpressionWordsGotor
from utils.handle import TextHandle

class SentenceParse(ModelPath):
    def __init__(self):
        # 获取具有“说”的意思的词列表
        self.wordsgotor = ExpressionWordsGotor()
        self.expression_words = self.wordsgotor(300)
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
        roles = self.get_rolelabel(words, postags, arcs)
        return {
            "words": words,
            "postags": postags,
            "ner": ner,
            "arcs": [(arc.head, arc.relation) for arc in arcs],
            "roles": [
                [role.index, [[arg.name, (arg.range.start, arg.range.end)] for arg in role.arguments]] for role in roles
            ],
        }

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

    def __init__(self, news):
        self.news = news

    def __call__(self):
        self.sentences = self.__handel(self.news)
        # print(self.sentences)
        self.sentences_goal, self.parse, self.expression_words = self.__get_expression_sentences(self.sentences)
        # print(self.expression_words, )
        # print(self.parse)
        self.ners = self.get_named_entity(self.parse, self.expression_words)
        # print(self.ners)
        self.contents = self.get_content(self.ners, self.parse)
        infos = [
            {
                'who': self.ners[i]['sbv'][1],
                'expression': self.ners[i]['hed'][1],
                'what': ''.join(self.contents[i]),
            } for i in self.contents.keys()
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

    def __get_expression_sentences(self, sentences):
        # 检测句子是否含有 说 的意思
        parse = {}
        expression_words = {}
        sentences_goal = {}
        for i, sen in enumerate(sentences):
            for word in self.sen_parse.expression_words:
                if word in sen:
                    sentences_goal[i] = sen
                    parse[i] = self.sen_parse(sen)
                    expression_words[i] = word
        return sentences_goal, parse, expression_words

    def get_named_entity(self, parse, expression_words):
        """获取 命名主体"""
        ners = defaultdict(dict)
        for i in parse.keys():
            ner = parse[i]['ner']
            words = parse[i]['words']
            arcs = parse[i]['arcs']
            word = expression_words[i]
            # print(words, arcs, word)
            if word not in words:
                continue
            hed_index = words.index(word)
            # print(hed_index)
            if 0 not in arcs[hed_index]:
                continue
            for j, (k, v) in enumerate(arcs):
                # print(k, v)
                if v == 'SBV':
                    sbv_index = j
                    if "S" in ner[sbv_index] or "B" in ner[sbv_index] or "I" in ner[sbv_index] or "E" in ner[sbv_index]:
                        ners[i] = {
                            'hed': (hed_index, word),
                            'sbv': (sbv_index, words[sbv_index])
                        }
        return ners

    def get_content(self, ners, parse):
        """获取 说 的内容"""
        contents = defaultdict(str)
        for i in ners.keys():
            words = parse[i]['words']
            hed_index = ners[i]['hed'][0]
            hed_index_next = hed_index + 1
            if words[hed_index_next] in ['"', "'", "“", "‘", ":", "：", ',', '，']:
                contents[i] = words[hed_index_next + 1:]
            elif words[hed_index_next] in ['。', "！", "？", "!", "?"]:
                contents[i] = words[:hed_index]
            else:
                contents[i] = words[hed_index_next:]
        return contents


if __name__ == '__main__':
    npa = Parse('香料店老板说今年的生意不太好')
    print(npa())

