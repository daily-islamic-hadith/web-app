import os
from unittest.mock import Mock

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['JWT_SECRET_KEY'] = 'test-signing-secret-with-at-least-32-bytes'
os.environ['SECRET_KEY'] = 'test-session-secret-with-at-least-32-bytes'
os.environ['DEFAULT_RATE_LIMIT'] = '3 per minute'

import pytest
import httpx
import requests

from hadith_app import app
from hadith_app.extensions import db, limiter
from hadith_app.service import hadith_service


@pytest.fixture(autouse=True)
def isolate_services(monkeypatch):
    def unexpected_call(*args, **kwargs):
        raise AssertionError('External services must be stubbed in tests')

    monkeypatch.setattr(requests.sessions.Session, 'request', unexpected_call)
    monkeypatch.setattr(httpx.Client, 'send', unexpected_call)
    monkeypatch.setattr(db, 'connect', unexpected_call)
    hadith_service.CACHED_HADITH_META.clear()
    monkeypatch.setattr(hadith_service, 'CACHED_HADITH_DATA_SET_SIZE', -1)
    limiter.reset()
    app.config.update(TESTING=True)
    yield
    db.close_connection()


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def hadith_fixture(monkeypatch):
    from hadith_app.routes import user_routes

    hadith = hadith_service.HadithDto('fixture-ref', 'حديث عربي <script>', 'English <script>')
    monkeypatch.setattr(user_routes, 'get_hadith_by_mode', Mock(return_value=hadith))
    monkeypatch.setattr(user_routes, 'get_hadith_by_reference', Mock(return_value=hadith))
    return hadith
