from flask import Flask
from dao.hadith_dao import Database

app = Flask(__name__)
app.config['DB'] = Database()

from .routes import user_routes
