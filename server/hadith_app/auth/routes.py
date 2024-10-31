from flask import request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token

from hadith_app.auth import auth_bp
from hadith_app.service import user_service
from .schemas import CredentialsSchema


@auth_bp.route('/get-token', methods=['POST'])
@cross_origin()
def generate_access_token():
    schema = CredentialsSchema()
    errors = schema.validate(request.form)
    if errors:
        return jsonify({"error": errors}), 400
    username = request.form.get('username')
    password = request.form.get('password')
    valid_credentials = user_service.validate_user_credentials(username, password)
    if valid_credentials:
        # TODO add roles to the token details to skip extra db check on every call.
        access_token = create_access_token(identity={'username': username})
        return jsonify(token=access_token), 200
    else:
        return jsonify({"error": "Invalid Credentials"}), 401
