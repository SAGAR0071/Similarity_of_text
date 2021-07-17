from flask_restful import Api, Resource
from pymongo import MongoClient
from flask import Flask, jsonify, request
import os
import json
import bcrypt
import spacy

app = Flask(__name__)

api = Api(app)

Client = MongoClient("mongodb://db:27017")

db = Client.Simlaritydb

users = db["users"]


def UserExist(username):
    if users.find({"username": username}).count() == 0:
        return False
    else:
        return True


class Register(Resource):

    def post(self):  # Post Data
        posteddata = request.get_json()
        username = posteddata["username"]
        password = posteddata["password"]
        if UserExist(username):
            retjson = {
                "status": 301,
                "msg": "invalid username"
            }
            return jsonify(retjson)
        hased_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        users.insert({
            "username": username,
            "password": hased_pw,
            "token": 6
        })
        retjson = {
            "status": 200,
            "msg": "successfully "

        }
        return jsonify(retjson)


# function for detect
def Verifypw(username, password):
    if not UserExist(username):
        return False
    hashed_pw = users.find({"username": username})[0]['password']
    print(hashed_pw)
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def num_token(username):
    tokens = users.find({"username": username})[0]['token']
    return tokens


class Detect(Resource):
    def post(self):

        posteddata = request.get_json()
        username = posteddata["username"]
        password = posteddata["password"]
        text1 = posteddata['text1']
        text2 = posteddata['text2']
        if not UserExist(username):
            retjson = {
                "status": 301,
                "msg": "user is not exist"
            }
            return jsonify(retjson)

        correct_pw = Verifypw(username, password)
        if not correct_pw:
            retJson = {
                "status": 302,
                "msg": "Invalid Password"

            }
            return jsonify(retJson)
        count = num_token(username)
        if count <= 0:
            retJson = {
                "status": 303,
                "msg": "You are out of token"
            }
            return jsonify(retJson)

        nlp = spacy.load("en_core_web_sm")  # calculate the edit distance
        text1 = nlp(text1)
        text2 = nlp(text2)
        # Ratio is a number btween 0 and 1 the closer to 1 ,the closer to 1 the more similar text1 and text2
        ratio = text1.similarity(text2)
        retJson = {
            'status': 200,
            'msg': "Similarity score calculated",
            'similarity': ratio

        }
        count = num_token(username)
        users.update({"username": username}, {
            "$set": {"token": count - 1}

        })
        return jsonify(retJson)


class Refill(Resource):
    def post(self):
        posteddata = request.get_json()
        username = posteddata["username"]
        password = posteddata["admin_pass"]
        refill_amount = posteddata["refillamount"]
        if not UserExist(username):
            retjson = {
                "status": 301,
                "msg": "user is not exist"
            }
            return jsonify(retjson)
        correct_pw = "abc21"
        if not correct_pw == password:
            retjson = {
                "status": 304,
                "msg": "admin is not exist"
            }
            return jsonify(retjson)
        current_tokens = num_token(username)
        users.update({"username":"username"}, {"$set": {"tokens": refill_amount + current_tokens}})
        retjson = {

            "status": 200,
            "msg": "Refilled Successfully"
        }
        return jsonify(retjson)

api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')
if __name__ == "__main__":
    app.run(host='0.0.0.0')
