from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
import login

client = MongoClient('mongodb+srv://snu910501:gkftndlTek1!@cluster0.rp2hlij.mongodb.net/?retryWrites=true&w=majority')
db = client.miniproject

app = Flask(__name__)
SECRET_KEY = "HANGHAE"

import jwt
import datetime
import hashlib
import random
import string


@app.route('/')
def home():
    return render_template('/loginpage.html')


@app.route('/signUp', methods=['POST'])
def signUp():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    check_id = login.id_check(id_receive)

    if (check_id != False):
        return jsonify({'result': 'fail', 'msg': '아이디가 중복됩니다.'})
    else:
        hash_pw = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        db.user.insert_one({'id': id_receive, 'pw': hash_pw, 'post': []})
        return jsonify({'result': 'success'})


@app.route('/login', methods=['POST'])
def user_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
    if result == None:
        return jsonify({'result': 'fail', 'msg': '이메일 또는 비밀번호가 잘못되었습니다.'})
    else:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3000)
        }
        encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # decoded_jwt = jwt.decode(encoded_jwt, SECRET_KEY, algorithms=['HS256'])
        # print(encoded_jwt)
        # print(id_receive)
        return jsonify({'result': 'success', 'token': encoded_jwt})


@app.route('/post', methods=['GET'])
def post():
    token_receive = request.cookies.get('token')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(payload)
    user_info_list = db.user.find({})
    user_post_list = []

    for x in user_info_list:
        user_post_list.append(x['post'])

    return jsonify({'result': 'success', 'data': user_post_list, 'token': payload})


@app.route('/main')
def main():
    return render_template('/mainpage.html')
    # return jsonify({'result':'success', 'token' : token_receive})


@app.route('/write', methods=['GET'])
def postPage():
    return render_template('/uploadpage.html')


@app.route('/post/upload', methods=['POST'])
def postupload():
    token_receive = request.cookies.get('token')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    url_receive = request.form.getlist('url_give[]')
    text_receive = request.form['text_give']
    address_receive = request.form['address_give']
    tag_receive = request.form.getlist('tag_give[]')
    post_id = "".join([random.choice(string.ascii_letters) for _ in range(10)])

    # db 유저 콜렉션에 포스트 업데이트
    db.user.update_one({'id': payload['id']}, {
        '$push': {'post': {'url': url_receive, 'text': text_receive, 'address': address_receive, 'tag': tag_receive,
                           'post_id': post_id}}})

    # db tag 콜렉션에 tag 업데이트
    for tag in tag_receive:
        if bool(db.tag.find_one({'tag': tag})) != False:
            db.tag.update_one({'tag': tag}, {'$push': {'post': post_id}})
        else:
            db.tag.insert_one({'tag': tag, 'post': [post_id]})
    return jsonify({'result': 'success'})


@app.route('/searchtag', methods=['POST'])
def searchTag():
    tag_receive = request.form['tag_give']

    tag = db.tag.find_one({'tag': tag_receive}, {'_id': False})
    return jsonify({'result': 'success', 'data': tag})


@app.route('/searchpost', methods=['POST'])
def searchPost():
    token_receive = request.cookies.get('token')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    postId_receive = request.form['postId_give']
    posts = []
    print(postId_receive)
    for data in db.user.find():
        for i in range(len(data['post'])):
            id = data['post'][i]['post_id']
            if postId_receive == id:
                print('들어갑니다')
                return jsonify({'result': 'success', 'data': data['post'][i], 'user_id': data['id'],'payload': payload})
            # else:
            #     return jsonify({'result':'fail'})
    return jsonify({'result': 'fail'})

# @app.route('/delPost', methods=['POST'])
# def delPost() :
#     postId_receive = request.form['postId_give']
#     for data in db.user.find():
#         for i in range(len(data['post'])):
#             id = data['post'][i]['post_id']
#             if postId_receive == id:
#                 db.user.delete_one({'id':data['post'][i]['id']})
#

if __name__ == '__main__':
    app.run('0.0.0.0', port=7000, debug=True)
