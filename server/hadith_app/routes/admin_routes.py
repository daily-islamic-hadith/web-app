from flask import jsonify, request
from flask_cors import cross_origin

from hadith_app import app
from hadith_app.auth.utils import role_required
from hadith_app.service.hadith_service import delete_today_hadith, generate_new_hadith_explanation


@app.route('/admin/api/delete-today-hadith')
@cross_origin()
@role_required('admin')
def delete_hadith_of_the_day():
    deleted = delete_today_hadith()
    if deleted:
        return jsonify(msg="Ok")
    else:
        return jsonify(error="Something Went Wrong!"), 400


@app.route('/admin/api/generate-hadith-explanation')
@cross_origin()
@role_required('admin')
def generate_hadith_explanation():
    hadith_ref_param = request.args.get('hadith_reference')
    if hadith_ref_param is None:
        return jsonify(error="Missing hadith reference"), 400
    generated = generate_new_hadith_explanation(hadith_ref_param)
    if generated:
        return jsonify(msg="Ok")
    else:
        return jsonify(error="Something Went Wrong!"), 400
