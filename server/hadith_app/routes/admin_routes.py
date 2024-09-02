from flask import jsonify
from flask_cors import cross_origin

from hadith_app import app
from hadith_app.auth.utils import role_required
from hadith_app.service.hadith_service import delete_today_hadith


@app.route('/admin/delete-today-hadith')
@cross_origin()
@role_required('admin')
def delete_hadith_of_the_day():
    deleted = delete_today_hadith()
    if deleted:
        return jsonify(msg="Ok")
    else:
        return jsonify(error="Something Went Wrong!"), 400
