from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient

client = MongoClient('mongodb+srv://snu910501:gkftndlTek1!@cluster0.rp2hlij.mongodb.net/?retryWrites=true&w=majority')
db = client.miniproject

app = Flask(__name__)
SECRET_KEY = "HANGHAE"

import hashlib

@app.route('/')
def home() :
    return render_template('/loginpage.html')

@app.route('/signUp', methods=['POST'])
def signUp():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    check_id = id_check(id_receive)

    if(check_id != False) :
        return jsonify({'result' : 'fail', 'msg':'아이디가 중복됩니다.'})
    else :
        hash_pw = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        db.user.insert_one({'id': id_receive, 'pw': hash_pw})
        return jsonify({'result' : 'success'})

def id_check(id) :
    id_check = bool(db.user.find_one({'id': id}, {'_id' : False}))
    return id_check





if __name__ == '__main__':
    app.run('0.0.0.0', port=7000, debug=True)

