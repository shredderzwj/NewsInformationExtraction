# -*- coding: utf-8 -*-


import os
from gensim.models.word2vec import Word2Vec, LineSentence
from collections import defaultdict
import json


class TrainWord2Vec(object):
    # 根据分好词的语料库进行词向量训练，并保存训练结果到本地
    def __init__(self, source, *args, **kwargs):
        """
        :param source: string or a file-like object
                        Path to the file on disk, or an already-open file object (must support `seek(0)`).
        :param args:  parameter of LineSentence
        :param kwargs:  parameter of LineSentence
        """
        self.line_sen = LineSentence(source, *args, **kwargs)

    def __call__(self, model_path, *args, **kwargs):
        """
        :param model_path: str Path of model that is saved to local(include filename)
        :param args:  parameter of Word2Vec
        :param kwargs:  parameter of Word2Vec
        :return: model
        """
        model = Word2Vec(self.line_sen, *args, **kwargs)
        model.save(model_path)
        return model


def get_related_words(initial_words, model, size=500, topn=10):
    """
    获取 相近词
    :param initial_words list
    :param model is the word2vec model.
    :return 
    """
    unseen = initial_words
    seen = defaultdict(int)
    while unseen and len(seen) < size:
        if len(seen) % 50 == 0:
            print('seen length : {}'.format(len(seen)))
        node = unseen.pop(0)
        new_expanding = [w for w, s in model.most_similar(node, topn=topn)]
        unseen += new_expanding
        seen[node] += 1
    return seen


if __name__ == '__main__':
    words_path = r'D:\NLPdata\corpus.words'
    model_path = r'D:\NLPdata\wiki_and_news.model'
    if os.path.exists(model_path):
        word2voc_model = Word2Vec.load(model_path)
    else:
        word2voc_model = TrainWord2Vec(words_path)
        word2voc_model(model_path, workers=8)

    related_words = get_related_words(['说', '说道', '表示', '讲'], word2voc_model, size=500, topn=10)
    words = sorted(related_words.items(), key=lambda x: x[1], reverse=True)
    words = list(zip(*words))[0]
    fp = open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'expression_words.json'), 'w')
    json.dump(words, fp)


