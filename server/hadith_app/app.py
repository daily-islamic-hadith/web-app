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


if __name__ == '__main__':
    app.run()
