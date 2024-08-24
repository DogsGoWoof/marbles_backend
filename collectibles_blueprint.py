import os
import jwt
from flask import Blueprint, jsonify, request, g
from db import get_db_connection
import psycopg2, psycopg2.extras

from auth_middleware import token_required

collectibles_blueprint = Blueprint('collectibles_blueprint', __name__)



@collectibles_blueprint.route('/profiles/<int:profile_id>/collectibles', methods=['GET'])
def profiles_collectibles_index(profile_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                       SELECT username, name, image, rating, count, condition, collectibles.id as id  FROM users
                       RIGHT JOIN collectibles ON collectibles.user_id = users.id
                       WHERE users.profile_id = %s;
                       """, (profile_id,))
        collectibles = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify(collectibles), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@collectibles_blueprint.route('/collectibles', methods=['GET'])
@token_required
def collectibles_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                       SELECT * FROM collectibles WHERE user_id = %s;
                       """, (g.user['id'],))
        collectibles = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify(collectibles), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    

@collectibles_blueprint.route('/collectibles', methods=['POST'])
@token_required
def create_collectible():
    try:
        new_collectible = request.json
        new_collectible["user_id"] = g.user["id"]
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO collectibles (user_id, name, image, rating, count, condition, date_obtained)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                        """,
                        (new_collectible['user_id'], new_collectible['name'], new_collectible['image'], new_collectible['rating'], new_collectible['count'], new_collectible['condition'], new_collectible["date_obtained"])
        )
        created_collectible = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify(created_collectible), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    

@collectibles_blueprint.route('/collectibles/<collectible_id>', methods=['GET'])
def show_collectible(collectible_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT * FROM collectibles WHERE id = %s;
            """,
            (collectible_id,))
        collectible = cursor.fetchall()
        if collectible is not None :
            return jsonify(collectible), 200
        else:
            return jsonify({"error": "collectible not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        connection.close()


@collectibles_blueprint.route('/collectibles/<collectible_id>', methods=['PUT'])
@token_required
def update_collectible(collectible_id):
    try:
        updated_collectible_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM collectibles WHERE collectibles.id = %s", (collectible_id,))
        collectible_to_update = cursor.fetchone()
        if collectible_to_update is None:
            return jsonify({"error": "collectible not found"}), 404
        connection.commit()
        if collectible_to_update["user_id"] is not g.user["id"]:
            return jsonify({"error": "Unuser_idized"}), 401
        cursor.execute("UPDATE collectibles SET name = %s, image = %s, rating = %s, count = %s, condition = %s, date_obtained = %s WHERE collectibles.id = %s RETURNING *",
                        (updated_collectible_data["name"], updated_collectible_data["image"], updated_collectible_data["rating"], updated_collectible_data["count"], updated_collectible_data["condition"], updated_collectible_data["date_obtained"], collectible_id))
        updated_collectible = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify(updated_collectible), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@collectibles_blueprint.route('/collectibles/<collectible_id>', methods=['DELETE'])
@token_required
def delete_collectible(collectible_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM collectibles WHERE collectibles.id = %s", (collectible_id,))
        collectible_to_delete = cursor.fetchone()
        if collectible_to_delete is None:
            return jsonify({"error": "collectible not found"}), 404
        connection.commit()
        if collectible_to_delete["user_id"] is not g.user["id"]:
            return jsonify({"error": "Unuser_idized"}), 401
        cursor.execute("DELETE FROM collectibles WHERE collectibles.id = %s", (collectible_id,))
        connection.commit()
        connection.close()
        return jsonify(collectible_to_delete), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500