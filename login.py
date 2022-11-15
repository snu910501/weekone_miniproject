from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient

client = MongoClient('mongodb+srv://snu910501:gkftndlTek1!@cluster0.rp2hlij.mongodb.net/?retryWrites=true&w=majority')
db = client.miniproject

import hashlib

def id_check(id) :
    id_check = bool(db.user.find_one({'id': id}, {'_id' : False}))
    return id_check
