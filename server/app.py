from flask import current_app
from . import app


@app.teardown_appcontext
def close_db(error):
    """
    Close the database connection at the end of the request.

    This function closes the database connection stored in the Flask app's configuration under
    the key 'DB' at the end of the request.

    Args:
        error (Exception): An optional error that occurred during the request.
    """
    db = current_app.config.get('DB')
    if db is not None:
        db.close_connection()


if __name__ == '__main__':
    app.run()
