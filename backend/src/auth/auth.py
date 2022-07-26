import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-dy086z0n.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'Coffee'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
@COMPLETE implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
# 7/26/22 #referenced the video/code from the lesson
# '13. Sending Tokens' to build this method
# https://learn.udacity.com/nanodegrees/nd0044/parts/cd0039/lessons/d266ef96-8da1-4dc0-b5b1-d6c3e4af9923/concepts/c9957a38-a6eb-40e0-addc-c794f2023ffb


def get_token_auth_header():
    # If the 'Authorization' not in the request, abort 401
    # 8/3/22 #Referenced the code in the Video from
    # '15. Practice - Applying Skills in Flask' min 3:35
    # https://learn.udacity.com/nanodegrees/nd0044/parts/cd0039/lessons/d266ef96-8da1-4dc0-b5b1-d6c3e4af9923/concepts/bb611ecd-2693-4556-a970-48128dba5c24
    if 'Authorization' not in request.headers:
        abort(401)
    else:
        # assign the bearer authorization header
        request_header = request.headers['Authorization']
        # assign the name to a variable
        bearer = request_header.split(' ')[0]
        # assign the token to a variable
        token = request_header.split(' ')[1]
    return token


'''
@COMPLETE implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload
    it should raise an AuthError if permissions are not included in the payload
    !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission
    string is not in the payload permissions array
    return true otherwise
'''
# 7/31/22 #referenced the video and code from the
# '4. Using RBAC in Flask' lesson to develop this method
# #https://learn.udacity.com/nanodegrees/nd0044/parts/cd0039/lessons/1e1c8e9d-61af-4a0a-b7d5-87e5becf9be7/concepts/b4d79d5c-3d79-43e6-93ca-0d750043a373


def check_permissions(permission, payload):
    # check if the permission is in the payload
    if permission in payload['permissions']:
        return True
    # else abort 403
    else:
        abort(403)


'''
@COMPLETE implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here:
    #https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
# 7/31/22 #referenced the code/graffiti voice overs from the
# '10. Practice - Validating Auth0 Tokens' lesson to build this method
# https://learn.udacity.com/nanodegrees/nd0044/parts/cd0039/lessons/d266ef96-8da1-4dc0-b5b1-d6c3e4af9923/concepts/ae26e42d-e380-4400-ae3f-c6d2ef65ef71


def verify_decode_jwt(token):
    # load the jwks.json url
    url = urlopen(f'https://{AUTH0_DOMAIN}' + "/.well-known/jwks.json")
    # convert the jwks.json response to json
    jwks = json.loads(url.read())

    # get the jwt token that needs to be verified
    header = jwt.get_unverified_header(token)

    # initialize the dictionary
    rsa = {}
    # for loop to build the rsa key
    for val in jwks['keys']:

        if val['kid'] == header['kid']:
            rsa = {
                'kty': val['kty'],
                'kid': val['kid'],
                'use': val['use'],
                'n': val['n'],
                'e': val['e']
            }
    # use the token, key, algorithm, audience, and issuer to build the payload
    payload = jwt.decode(token,
                         rsa,
                         algorithms=ALGORITHMS,
                         audience=API_AUDIENCE,
                         issuer="https://" + AUTH0_DOMAIN + "/")
    # if payload is none, abort 401
    if payload is None:
        abort(401)
    # return the payload
    else:
        return payload


'''
@COMPLETE implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims
    and check the requested permission return the decorator which
    passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
