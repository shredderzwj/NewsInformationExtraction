# -*- coding: utf-8 -*-


from flask import Flask, render_template, g, session, url_for, request
from flask_script import Manager
import re
import base64

from orm import ExpressionWordsOperate
from parse_news import Parse


app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "klsajdghgkljasglkhasdfhasdgasdfg"
manager = Manager(app)


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
    """
    return render_template('index.html', fly_str=base64_encode(fly_str))


@app.route('/extra', methods=['GET', 'POST'])
def extra():
    if request.method == 'GET':
        news = request.args.get('s')
    elif request.method == 'POST':
        news = request.form['news']
    else:
        news = ''
    if not news:
        return '<script>alert("没有输入内容！")</script>'
    parse = Parse(news, ExpressionWordsOperate()[:])
    infos = parse()
    if isinstance(infos, list):
        infos_type = "list"
    else:
        infos_type = 'str'
    return render_template('extra.html', infos=infos, infos_type=infos_type, fly_str=base64_encode(news[:500]))


@app.route('/expression-words-operate', methods=['GET', 'POST'])
def expression_words_operate():
    pass


@app.route('/fly-words')
def fly_words():
    fly_str_base64 = request.args.get('s')
    fly_str = ''
    try:
        fly_str = base64_decode(fly_str_base64)
    except :
        pass
    if not fly_str:
        fly_str = fly_str_base64
    if not fly_str:
        fly_str = "没有内容"
    return render_template('fly_words.html', **get_fly_words_list(fly_str))


def get_fly_words_list(fly_str):
    fly_words = []
    for x in re.findall(r'\w+', fly_str):
        fly_words += Parse.sen_parse.get_words(x)
    return {
        'wordList': fly_words,
    }


def base64_encode(s):
    return base64.encodebytes(s.encode()).decode().replace('\n', '').replace('/', '_').replace("+", '-')


def base64_decode(base64_str):
    base64_str = base64_str.replace('_', '/').replace("-", '+')
    return base64.decodebytes(base64_str.encode()).decode()


if __name__ == "__main__":
    manager.run()
