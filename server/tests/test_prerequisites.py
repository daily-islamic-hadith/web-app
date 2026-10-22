from unittest.mock import Mock

import bcrypt
import pytest
from flask_limiter import RateLimitExceeded

from hadith_app import app
from hadith_app.extensions import db
from hadith_app.routes import user_routes
from hadith_app.service.user_service import validate_password


@pytest.mark.parametrize('path', ['/api/today-hadith', '/api/random-hadith'])
def test_legacy_hadith_routes(client, hadith_fixture, path):
    response = client.get(path)
    assert response.status_code == 200
    assert response.json['reference'] == hadith_fixture.reference
    assert user_routes.get_hadith_by_mode.call_args.args[1] is None


def test_handlers_registered_by_package_entrypoint():
    handler = app.error_handler_spec[None][429][RateLimitExceeded]
    assert handler.__name__ == 'ratelimit_handler'
    assert any(fn.__name__ == 'close_db' for fn in app.teardown_appcontext_funcs)


def test_teardown_closes_database(monkeypatch):
    close = Mock()
    monkeypatch.setattr(db, 'close_connection', close)
    with app.app_context():
        pass
    close.assert_called_once()


@pytest.mark.parametrize('password', ['a' * 73, '😀' * 20])
def test_oversized_password_is_invalid(password):
    existing_hash = bcrypt.hashpw(b'a' * 72, bcrypt.gensalt(rounds=4))
    assert validate_password(existing_hash, password) is False


@pytest.mark.parametrize('bad_hash', [b'broken', '', None])
def test_malformed_password_hash_is_invalid(bad_hash):
    assert validate_password(bad_hash, 'password') is False


def test_existing_hash_and_password_boundary():
    password = 'a' * 72
    existing_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4))
    assert validate_password(existing_hash, password) is True
    assert validate_password(existing_hash, 'b' * 72) is False


def test_unicode_password_route_returns_401(client, monkeypatch):
    from hadith_app.models import User
    from hadith_app.service import user_service

    user = User(1, 'tester', bcrypt.hashpw(b'password', bcrypt.gensalt(rounds=4)), [])
    monkeypatch.setattr(user_service, 'fetch_user_by_username', Mock(return_value=user))
    response = client.post('/auth/api/get-token', data={'username': 'tester', 'password': '😀' * 20})
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid Credentials'}


@pytest.mark.parametrize('path,is_json', [('/api/random-hadith', True), ('/', False)])
def test_custom_rate_limit_response(client, hadith_fixture, path, is_json):
    responses = [client.get(path) for _ in range(4)]
    assert [r.status_code for r in responses] == [200, 200, 200, 429]
    response = responses[-1]
    if is_json:
        assert response.is_json
        assert response.json == {'error': 'Too many requests. Please try again later.'}
    else:
        assert response.mimetype == 'text/html'
        assert b'Too many requests. Please try again later.' in response.data
