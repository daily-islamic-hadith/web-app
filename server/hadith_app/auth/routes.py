from flask import request, jsonify, current_app
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token
from flask_principal import identity_changed, Identity

from hadith_app.auth import auth_bp
from hadith_app.models import User


@auth_bp.route('/get-token', methods=['POST'])
@cross_origin()
def generate_access_token():
    username = request.form.get('username')
    password = request.form.get('password')
    valid_credentials = User.validate_user_credentials(username, password)
    if valid_credentials:
        access_token = create_access_token(identity={'username': username})
        # Signal identity change (required for flask_principal)
        identity_changed.send(current_app, identity=Identity(username))
        return jsonify(token=access_token), 200
    else:
        return jsonify({"error": "Invalid Credentials"}), 401
