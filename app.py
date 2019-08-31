# -*- coding: utf-8 -*-


from flask import Flask, render_template, session, url_for, request, redirect
from flask_script import Manager
import re
import base64
import hashlib
from collections import defaultdict


from orm import ExpressionWordsOperate
from parse_news import Parse


app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "==30=05=/2@#sdf%#f@$a-sd@!##$@#$8!@#$!0@%!@#sdf21fg5sd44fa23"
manager = Manager(app)
user = 'alpha_zero'
pwd = '978ff1afe3a13140a9c7193d6f11d29030f06238043a5c646e293e6be3cb570b'


def check_login(f):
    def wrap(*args, **kwargs):
        if session.get('user') == user and session.get('pwd') == pwd:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    wrap.__name__ = f.__name__    # 将传入函数的 __name__ 属性值赋值给闭包函数，以便 url_for 函数捕获地址。
    return wrap


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
@check_login
def expression_words_operate():
    operate = ExpressionWordsOperate()
    info = defaultdict(list)
    if request.method == "POST":
        words = request.form['s'].strip().split(' ')
        words = [word for word in words if len(word) < 5]
        bools = operate.add_words(words)
        words_added = [word for i, word in enumerate(words) if bools[i]]
        if words_added:
            info['add'] = words_added
    else:
        try:
            _id = int(request.args.get("del"))
            word = operate.del_word_by_id(_id)
            print(_id, word)
            if word:
                info['delete'].append(word)
        except:
            pass
    print(info)
    words_dict = operate.get_all()
    return render_template('manager.html', words=words_dict, info=info)


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


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        user_get = request.form['user']
        pwd_get = request.form['pwd']
        pwd_hash = hashlib.sha256(pwd_get.encode()).hexdigest()
        if user == user_get and pwd == pwd_hash:
            session['user'] = user
            session['pwd'] = pwd_hash
            return redirect(url_for("expression_words_operate"))
        else:
            return redirect(request.url)
    else:
        if session.get('user') == user and session.get('pwd') == pwd:
            return redirect(url_for("expression_words_operate"))
        return render_template('login.html')


@app.route('/logout')
def logout():
    session['user'] = ""
    session['pwd'] = ""
    return redirect(url_for('login'))


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
