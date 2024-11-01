from flask import jsonify, request, render_template
from flask_limiter import RateLimitExceeded

from hadith_app import app
from hadith_app.extensions import db


@app.teardown_appcontext
def close_db(error):
    """
    Close the database connection at the end of the request.

    Args:
        error (Exception): An optional error that occurred during the request.
    """
    if db is not None:
        db.close_connection()


# Custom error handler for rate limit exceeded
@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    if '/api/' in request.path:
        return jsonify(error="Too many requests. Please try again later."), 429
    return render_template("index.html", error="Too many requests. Please try again later."), 429



if __name__ == '__main__':
    app.run()
