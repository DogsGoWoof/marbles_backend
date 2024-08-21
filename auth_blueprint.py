import os
import jwt
import bcrypt
import psycopg2, psycopg2.extras
from flask import Blueprint, jsonify, request, session, redirect, url_for, render_template
from db import get_db_connection

authentication_blueprint = Blueprint('authentication_blueprint', __name__)

@authentication_blueprint.route('/auth/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        try:
            new_user_data = request.get_json()
            connection = get_db_connection()
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE username = %s;", (new_user_data["username"],))
            existing_user = cursor.fetchone()
            if existing_user:
                cursor.close()
                return jsonify({"error": "Username already taken"}), 400
            hashed_password = bcrypt.hashpw(bytes(new_user_data["password"], 'utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id, username", (new_user_data["username"], hashed_password.decode('utf-8')))
            created_user = cursor.fetchone()
            connection.commit()
            token = jwt.encode(created_user, os.getenv('JWT_SECRET'))
            return jsonify({"token": token, "user": created_user}), 201
        except Exception as error:
            return jsonify({"error": str(error)}), 401
        finally:
            connection.close()

    return render_template('auth/signup.html')

@authentication_blueprint.route('/auth/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        print(request.headers['Content-Type'])
        if request.headers['Content-Type'] == 'application/json':
            print('JSON')
        elif request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            print("why is it like this?")
        try:

            if request.headers['Content-Type'] == 'application/json':
                sign_in_form_data = request.get_json()
            elif request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
                sign_in_form_data = request.form.to_dict()

            connection = get_db_connection()

            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE username = %s;", (sign_in_form_data["username"],))
            existing_user = cursor.fetchone()

            if existing_user is None:
                return jsonify({"error": "Invalid credentials."}), 401
            password_is_valid = bcrypt.checkpw(bytes(sign_in_form_data["password"], 'utf-8'), bytes(existing_user["password"], 'utf-8'))
            
            if not password_is_valid:
                return jsonify({"error": "Invalid credentials."}), 401
            
            token = jwt.encode({"username": existing_user["username"], "id": existing_user["id"]}, os.getenv('JWT_SECRET'))
            
            session.clear()
            session['token'] = token
            return render_template('base.html')
        except Exception as error:
            return jsonify({"error": "Invalid credentials."}), 401

    return render_template('auth/signin.html')

@authentication_blueprint.route('/auth/signout')
def signout():
    session.clear()
    return redirect(url_for('home'))