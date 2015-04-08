import models
import urlparse

from flask import Flask
from flask.ext.restful import reqparse, abort, fields, marshal, marshal_with, Resource
from flask.json import jsonify
from tzundoku import tzundoku, db, tzundoku_api

API_VERSION=1
API_PATH="/api"

user_fields={
    'id' : fields.Integer,
    'username' : fields.String,
    'email' : fields.String
}

def make_error(status, error_code, developer_message, user_message=None, info=None):
    response_dict={
        'status': status,
        'errorCode': error_code,
        'developerMessage': developer_message,
    }
    for i in [(user_message, "userMessage"), (info, "info")]:
        if i[0] is not None:
            response_dict.update(i[1], i[0])
    response = jsonify(response_dict)
    response.status_code = status
    return response

class getUsers(Resource):
    @marshal_with(user_fields)
    def get(self):
        users=models.User.query.all()
        return users

class getUser(Resource):
    @marshal_with(user_fields)
    def get(self, username):
        users=models.User.query.filter_by(username=username).all()
        return users

doku_fields={
    'title' : fields.String,
    'id' : fields.Integer
}

doku_parser=reqparse.RequestParser()
doku_parser.add_argument('id', type=int)
doku_parser.add_argument('title', type=str)

class getDokus(Resource):
    @marshal_with(doku_fields)
    def get(self):
        args=doku_parser.parse_args()
        result=models.Doku.query
        for field in ["id", "title"]:
            value=getattr(args, field)
            if value is not None:
                result=result.filter_by(**{field : value})
        
        dokus=result.all()

        return dokus

class useDoku(Resource):
    def delete(self):
        args=doku_parser.parse_args()
        id=args.id
        dokus=models.Doku.query.filter_by(id=id).all()
        if len(dokus)==0:
            return make_error(404, 101, "Doku with id {} not found".format(id))
        elif len(dokus)==1:
            doku=dokus[0]
            doku.delete()
            return marshal(doku, doku_fields)
        else:
            return make_error(404, 102, "There are more than one dokus with id {}".format(id))

    @marshal_with(doku_fields)
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str)
        args=parser.parse_args()
        title=args.title
        doku=models.Doku(title=title)
        db.session.add(doku)
        db.session.commit()
        return doku, 201

def make_url(s):
    return "/".join([API_PATH, "v{}".format(API_VERSION), s])

tzundoku_api.add_resource(getUsers, make_url('users'))
tzundoku_api.add_resource(getUser, make_url('users/<string:username>'))
tzundoku_api.add_resource(getDokus, make_url('dokus'))
tzundoku_api.add_resource(useDoku, make_url('doku'))
