from flask import Flask
from hadith_app.dao.hadith_dao import Database

app = Flask(__name__)
app.config['DB'] = Database()

from hadith_app.routes import user_routes
