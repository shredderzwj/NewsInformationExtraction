# -*- coding: utf-8 -*-


from flask import Flask, render_template, g, session, url_for, request
import jieba
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
        人工智能（Artificial Intelligence），英文缩写为AI。它是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。
        natural language processing
        NLP是计算机科学领域与人工智能领域中的一个重要方向。它研究能实现人与计算机之间用自然语言进行有效通信的各种理论和方法。它是一门融语言学、计算机科学、数学于一体的科学。因此，这一领域的研究将涉及自然语言，即人们日常使用的语言，所以它与语言学的研究有着密切的联系，但又有重要的区别。自然语言处理并不是一般地研究自然语言，而在于研制能有效地实现自然语言通信的计算机系统，特别是其中的软件系统。因而它是计算机科学的一部分。
        新闻人物言论自动提取。 
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


def get_fly_words(fly_str):
    fly_words = []
    for x in re.findall(r'\w+', fly_str):
        fly_words += jieba.lcut(x)
    return {
        'wordList': fly_words,
    }


if __name__ == "__main__":
    A = 'Shredder'
    app.run(host='0.0.0.0')
