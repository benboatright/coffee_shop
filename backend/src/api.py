from crypt import methods
import os
from urllib import response
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@COMPLETE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@COMPLETE implement endpoint
    GET /drinks
    it should be a public endpoint
    it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''
# 7/20/22 #followed documentation to get started
# #https://flask.palletsprojects.com/en/2.1.x/quickstart/
# 7/20/22 #followed Caryn's __init__.py file in 6_Final_Starter folder 
# from 'API Development and Documentation' module 


@app.route('/drinks', methods=['GET'])
def get_drinks():
    # query all the drinks in the database
    drinks = Drink.query.all()
    # check if there are drinks
    if drinks is not None:
        # return True for success and the short list of all the drinks
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks] # 7/20/22 #followed Caryn's __init__.py file in 6_Final_Starter folder from 'API Development and Documentation' module to get the drinks to display
        })
    # if there are no drinks, abort 404
    else:
        abort(404)


'''
@COMPLETE implement endpoint
    GET /drinks-detail
    *it should require the 'get:drinks-detail' permission*
    it should contain the drink.long() data representation
    returns status code 200 and json
    {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''
# 7/31/22 #used the video and code from the
# '4. Using RBAC in Flask' lesson to add the @requires_auth wrapper
# #https://learn.udacity.com/nanodegrees/nd0044/parts/cd0039/lessons/1e1c8e9d-61af-4a0a-b7d5-87e5becf9be7/concepts/b4d79d5c-3d79-43e6-93ca-0d750043a373

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    # query all the drinks in the databse
    drinks = Drink.query.all()
    # check to see if there are drinks
    if drinks is not None:
        # retrun True for success and the long list of all the drinks
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks] # 7/31/22 # followed Caryn's __init__.py file in 6_Final_Starter folder from 'API Development and Documentation' module to get the drinks to display using list comprehension
        })
    # if no drnks, abort 404
    else:
        abort(404)


'''
@COMPLETE implement endpoint
    POST /drinks
    it should create a new row in the drinks table
    it should require the 'post:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json
    {"success": True, "drinks": drink} where drink an array
    containing only the newly created drink
    or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(token):
    # get the request
    request_body = request.get_json() # 7/31/22 # followed Caryn's __init__.py file in 6_Final_Starter folder from 'API Development and Documentation' module to remind myself how to get the request data
    # check if body is none
    if request_body is None or request_body == '':
        abort(404)
    else:
        # retreive the title and the recipe
        new_title = request_body.get("title") # 7/31/22 # followed Caryn's init__.py file in 6_Final_Starter folder from 'API Development and Documentaion' module to extract the title from the request body
        # 7/31/22 #i tried using body.get(" ") method from Caryn's __init__.py file in 6_Final_Starter folder from 'API Development and Documentation' module but kept getting error.
        # Vinicius recommedned this code to another user
        # #https://knowledge.udacity.com/questions/510654
        new_recipe = json.dumps(request_body.get("recipe"))
        # create a new instance
        drink = Drink(title=new_title, recipe=new_recipe)
        # insert the new instance
        drink.insert()
        return jsonify({
            'success': True,
            'drink': drink.long()
        })


'''
@COMPLETE implement endpoint
    PATCH /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should update the corresponding row for <id>
    it should require the 'patch:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json
    {"success": True, "drinks": drink} where drink
    an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(token, id):
    # retreive the drink from the table
    drink = Drink.query.get(id)
    # retreive the body from the request
    request_body = request.get_json() # 7/31/22 #followed Caryn's __init__.py file in 6_Final_Starter folder from 'API Development and Documentation' module to get the request body
    # check to make sure the drink id is in the table
    # and the body has content
    if drink is None:
        abort(404)
    if request_body is not None:
        # get the new title
        new_title = request_body.get("title") # 7/31/22 # followed Caryn's __init__.py file in 6_Final_Starter folder from 'API Development and Documentation' module to get the title from the body
        # get the new recipe
        new_recipe = json.dumps(request_body.get("recipe")) # 7/31/22 # Vinicius recommedned this code to another user #https://knowledge.udacity.com/questions/510654
        # update the title
        if new_title is not None:
            drink.title = new_title
        # update the recipe
        if new_recipe is not None:
            drink.recipe = new_recipe
        # make the update
        drink.update()
        # get the updated record
        drink_updated = Drink.query.get(id)
        # return the success
        return jsonify({
            'success': True,
            'drinks': [drink_updated.long()]
        })


'''
@COMPLETE implement endpoint
    DELETE /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should delete the corresponding row for <id>
    it should require the 'delete:drinks' permission
    returns status code 200 and json
    {"success": True, "delete": id} where id is
    the id of the deleted record
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token, id):
    # identify the drink based on the id in the route
    drink = Drink.query.get(id)
    # if the drink is not in the database, abort 404
    if drink is None:
        abort(404)
    else:
        # delete the drink from the database table
        drink.delete()
        # return the following
        return jsonify({
            'success': True,
            'delete': id
        })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@COMPLETE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
# I followed the code above


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404

@app.errorhandler(401)
def no_credentials(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': "no credentials"
    }), 401

@app.errorhandler(403)
def no_permission(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'permission not included'
    }), 403
'''
@COMPLETE implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
