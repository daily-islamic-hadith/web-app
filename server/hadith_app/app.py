# Direct script execution needs the server directory on the import path.
if __name__ == '__main__' and not __package__:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import jsonify, request
from flask_limiter import RateLimitExceeded

from hadith_app.extensions import db
from hadith_app.routes.helper.response_helper import get_template_response


def close_db(error):
    """Close any remaining connection when the application context ends."""
    db.close_connection()


def ratelimit_handler(error):
    message = "Too many requests. Please try again later."
    if '/api/' in request.path:
        return jsonify(error=message), 429
    return get_template_response(request, {"error": message, "status_code": 429}, False)


def register_handlers(app):
    app.teardown_appcontext(close_db)
    app.register_error_handler(RateLimitExceeded, ratelimit_handler)


if __name__ == '__main__':
    from hadith_app import app

    app.run()
