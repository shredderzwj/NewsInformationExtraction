# -*- coding: utf-8 -*-


from flask import Flask, render_template, g, session, url_for, request
import re
from parse_news import Parse


app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "klsajdghgkljasglkhasdfhasdgasdfg"


@app.before_first_request
def init_data():
    pass


@app.before_request
def get_data():
    pass


@app.route('/')
def index():
    fly_str = """
        新闻人物言论自动提取。 
        新闻人物言论即是在报道的新闻中，某个人物、团体或机构在某个时间、某个地点表达某种观点、意见或态度。
        面对互联网信息量的不断扩张，用户迫切地需要自动化的信息获取工具来帮助在海量的信息源中迅速找到和获得真正所需的信息。主要相关方面的研究有自动摘要、关键词提取以及人物言论的自动提取，这些都可以帮助用户快速准确的获取其所需的真正信息，节省用户时间，提高用户体验。其中新闻人物言论自动提取就可以帮助用户在新闻阅读、观点总结中能够发挥较大的辅助作用。
    """
    return render_template('index.html', **get_fly_words(fly_str))


@app.route('/extra', methods=['GET', 'POST'])
def extra():
    news = request.form['news']
    if not news:
        return '<script>alert("没有输入内容！")</script>'
    parse = Parse(news)
    infos = parse()
    if isinstance(infos, list):
        infos_type = "list"
    else:
        infos_type = 'str'
    return render_template('extra.html', infos=infos, infos_type=infos_type, **get_fly_words(news))


@app.route('/expression-words-operate', methods=['GET', 'POST'])
def expression_words_operate():
    pass


def get_fly_words(fly_str):
    fly_words = []
    for x in re.findall(r'\w+', fly_str):
        fly_words += Parse.sen_parse.get_words(x)
    return {
        'wordList': fly_words,
    }


if __name__ == "__main__":
    A = 'Shredder'
    app.run()
