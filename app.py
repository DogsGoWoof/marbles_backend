import os
import jwt
import psycopg2, psycopg2.extras
import bcrypt
from flask import Flask, jsonify, request, g, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# from auth_middleware import token_required

from auth_blueprint import authentication_blueprint
from collectibles_blueprint import collectibles_blueprint

load_dotenv()

app = Flask(__name__)
app.register_blueprint(authentication_blueprint)
app.register_blueprint(collectibles_blueprint)
CORS(app)


@app.route('/hello')
def home():
    return '<h1>Hello, World! - from Flask</h1>'


if __name__ == '__main__':
    app.run()
