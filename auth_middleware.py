from functools import wraps
from flask import request, jsonify, g, session
import jwt
import os


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
            # using React fontend
        authorization_header = request.headers.get('Authorization')
            # # #
            # using session flask frontend
        # authorization_header = session['token']
        print(authorization_header)
        if authorization_header is None:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            token = authorization_header.split(' ')[1]
            token_data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
            # token_data = jwt.decode(authorization_header, os.getenv('JWT_SECRET'), algorithms=["HS256"])
                        # jwt.decode(<JWT>, <JWT string used to encode>, algorithms=<hashing algorithm used>)
            g.user = token_data
                # g assigned key of ['user'] that holds token_data object
                    # token_data is JWT decoded back into user's username and id ( I think? )
        except Exception as error:
            return jsonify({"error": str(error)}), 500
        return f(*args, **kwargs)
    return decorated_function