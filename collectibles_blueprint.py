import os
import jwt
from flask import Blueprint, jsonify, request, g, render_template, url_for, session, redirect
from db import get_db_connection
import psycopg2, psycopg2.extras

from auth_middleware import token_required

from datetime import datetime

collectibles_blueprint = Blueprint('collectibles_blueprint', __name__)

@collectibles_blueprint.route('/collectibles', methods=['GET'])
def collectibles_index():

    if session:
        g.user = jwt.decode(session['token'], os.getenv('JWT_SECRET'), algorithms=["HS256"])
    else:
        return render_template('base.html')
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                       SELECT * FROM collectibles WHERE collectibles.user_id = g.user.id;
                       """)
        collectibles = cursor.fetchall()
        connection.commit()
        connection.close()
        return render_template('collectibles/index.html', collectibles=collectibles)
    except Exception as error:
        return jsonify({"error": str(error)}), 500