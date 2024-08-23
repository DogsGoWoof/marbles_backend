import os
import jwt
from flask import Blueprint, jsonify, request, g
from db import get_db_connection
import psycopg2, psycopg2.extras

from auth_middleware import token_required

profiles_blueprint = Blueprint('profiles_blueprint', __name__)


@profiles_blueprint.route('/profiles', methods=['GET'])
def profiles_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                       SELECT * FROM profiles;
                       """)
        profiles = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify(profiles), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    

@profiles_blueprint.route('/profiles', methods=['POST'])
@token_required
def create_profile():
    try:
        new_profile = request.json
        new_profile["user_id"] = g.user["id"]
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO profiles (user_id, name, image, collection, about, favourite, is_private)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                        """,
                        (new_profile['user_id'], new_profile['name'], new_profile['image'], new_profile['collection'], new_profile['about'], new_profile['favourite'], new_profile['is_private'])
        )
        created_profile = cursor.fetchone()
        connection.commit()
        print(created_profile)
        cursor.execute("""
                        UPDATE users SET profile_id = %s WHERE users.id = %s
                       """,
                       (created_profile['id'], g.user['id'])
                       )
        
        print(created_profile)
        connection.commit()
        connection.close()
        return jsonify(created_profile), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    

@profiles_blueprint.route('/profiles/<profile_id>', methods=['GET'])
def show_profile(profile_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT * FROM profiles WHERE id = %s;
            """,
            (profile_id,)
            )
        profile = cursor.fetchall()
        if profile is not None :
            return jsonify(profile), 200
        else:
            return jsonify({"error": "profile not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()


@profiles_blueprint.route('/profiles/<profile_id>', methods=['PUT'])
@token_required
def update_profile(profile_id):
    try:
        updated_profile_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM profiles WHERE profiles.id = %s", (profile_id,))
        profile_to_update = cursor.fetchone()
        if profile_to_update is None:
            return jsonify({"error": "profile not found"}), 404
        connection.commit()
        if profile_to_update["user_id"] is not g.user["id"]:
            return jsonify({"error": "Unuser_idized"}), 401
        cursor.execute("""
                       UPDATE profiles SET name = %s, image = %s, collection = %s, about = %s, favourite = %s, is_private = %s WHERE profiles.id = %s RETURNING *
                       """,
                       (updated_profile_data["name"], updated_profile_data["image"], updated_profile_data["collection"], updated_profile_data["about"], updated_profile_data["favourite"], updated_profile_data["is_private"], profile_id)
                        )
        updated_profile = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify(updated_profile), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@profiles_blueprint.route('/profiles/<profile_id>', methods=['DELETE'])
@token_required
def delete_profile(profile_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM profiles WHERE profiles.id = %s", (profile_id,))
        profile_to_delete = cursor.fetchone()
        if profile_to_delete is None:
            return jsonify({"error": "profile not found"}), 404
        connection.commit()
        if profile_to_delete["user_id"] is not g.user["id"]:
            return jsonify({"error": "Unuser_idized"}), 401
        cursor.execute("DELETE FROM profiles WHERE profiles.id = %s", (profile_id,))
        connection.commit()
        cursor.execute("UPDATE users SET profile_id = null WHERE users.id = profile_to_delete['user_id]")
        connection.close()
        return jsonify(profile_to_delete), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
