from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import bcrypt
import jwt
import pytest
from flask_jwt_extended import create_access_token

from hadith_app import app
from hadith_app.extensions import limiter
from hadith_app.models import User
from hadith_app.service import user_service


@pytest.fixture
def user(monkeypatch):
    user = User(1, 'tester', bcrypt.hashpw(b'password', bcrypt.gensalt(rounds=4)), ['admin'])
    monkeypatch.setattr(user_service, 'fetch_user_by_username', Mock(return_value=user))
    return user


def token_for_user(expires=None):
    with app.app_context():
        return create_access_token(identity={'username': 'tester'}, expires_delta=expires)


def test_login_token_and_admin(client, user, monkeypatch):
    from hadith_app.routes import admin_routes
    delete = Mock(return_value=True)
    monkeypatch.setattr(admin_routes, 'delete_today_hadith', delete)
    response = client.post('/auth/api/get-token', data={'username': 'tester', 'password': 'password'})
    assert response.status_code == 200
    token = response.json['token']
    claims = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
    assert claims['sub'] == 'tester'
    assert claims['exp'] - claims['iat'] == 180
    response = client.get('/admin/api/delete-today-hadith', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    delete.assert_called_once()


@pytest.mark.parametrize('case,status', [('missing', 401), ('expired', 401), ('signature', 401), ('deleted', 401), ('non_admin', 403)])
def test_protected_route_errors(client, user, monkeypatch, case, status):
    token = token_for_user(timedelta(seconds=-1) if case == 'expired' else None)
    if case == 'signature':
        claims = {'sub': 'tester', 'exp': datetime.now(timezone.utc) + timedelta(minutes=3)}
        token = jwt.encode(claims, 'different-signing-key-with-at-least-32-bytes', algorithm='HS256')
    if case == 'deleted':
        monkeypatch.setattr(user_service, 'fetch_user_by_username', Mock(return_value=None))
    if case == 'non_admin':
        user.roles = []
    headers = {} if case == 'missing' else {'Authorization': f'Bearer {token}'}
    headers['Origin'] = 'https://example.org'
    response = client.get('/admin/api/delete-today-hadith', headers=headers)
    assert response.status_code == status
    assert response.headers['Access-Control-Allow-Origin'] == headers['Origin']


@pytest.mark.parametrize('data', [{}, {'username': '', 'password': ''}, {'username': 'ab', 'password': 'password'},
    {'username': 'a' * 21, 'password': 'password'}, {'username': 'tester', 'password': '1234567'},
    {'username': 'tester', 'password': 'a' * 21}, {'username': 'tester', 'password': 'password', 'unknown': 'field'},
    {'username': 'tester', 'password': 'wrongpass'}])
def test_invalid_forms_return_401(client, user, data):
    response = client.post('/auth/api/get-token', data=data)
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid Credentials'}


@pytest.mark.parametrize('username,password', [('abc', 'a' * 8), ('u' * 20, 'p' * 20), ('مستخدم', 'كلمةمرور')])
def test_valid_schema_boundaries(username, password):
    from hadith_app.auth.schemas import CredentialsSchema
    assert CredentialsSchema().validate({'username': username, 'password': password}) == {}


@pytest.mark.parametrize('query,status', [('fetch-mode=daily', 200), ('fetch-mode=random', 200), ('', 400),
    ('fetch-mode=wrong', 400), ('fetch-mode=daily&lang=zz', 400), ('fetch-mode=daily&lang=AR', 200)])
def test_fetch_api(client, hadith_fixture, query, status):
    response = client.get('/api/fetch-hadith?' + query)
    assert response.status_code == status
    assert response.is_json


@pytest.mark.parametrize('path', ['/', '/hadith/fixture-ref', '/privacy-policy'])
def test_pages(client, hadith_fixture, path):
    response = client.get(path)
    assert response.status_code == 200
    assert response.mimetype == 'text/html'
    if path != '/privacy-policy':
        assert 'حديث عربي &lt;script&gt;' in response.text
        assert 'English &lt;script&gt;' in response.text


@pytest.mark.parametrize('ua,marker', [
    ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36', 'id="chrome-btn"'),
    ('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0', 'id="firefox-btn"'),
    ('Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1', 'id="summary_mob_title"'),
])
def test_user_agent_template_branches(client, hadith_fixture, ua, marker):
    response = client.get('/', headers={'User-Agent': ua})
    assert marker in response.text


def test_json_provider(hadith_fixture):
    value = {'hadith': hadith_fixture, 'time': datetime(2026, 10, 22, 12, 30)}
    output = app.json.loads(app.json.dumps(value))
    assert output['time'] == '2026-10-22T12:30:00'
    assert output['hadith']['hadithArabic'] == hadith_fixture.hadithArabic
    assert 'bookName' not in output['hadith']


def test_limiter_route_client_separation_and_reset(client, hadith_fixture):
    path = '/api/today-hadith'
    assert [client.get(path).status_code for _ in range(4)] == [200, 200, 200, 429]
    assert client.get('/api/random-hadith').status_code == 200
    assert client.get(path, environ_overrides={'REMOTE_ADDR': '192.0.2.1'}).status_code == 200
    limiter.reset()
    assert client.get(path).status_code == 200


def test_limiter_window_expires(client, hadith_fixture, monkeypatch):
    import time
    current_time = [time.time()]
    monkeypatch.setattr(time, 'time', lambda: current_time[0])
    path = '/api/today-hadith'
    assert [client.get(path).status_code for _ in range(4)] == [200, 200, 200, 429]
    current_time[0] += 61
    assert client.get(path).status_code == 200


def test_missing_reference_and_fetch_error(client, monkeypatch):
    from hadith_app.routes import user_routes
    monkeypatch.setattr(user_routes, 'get_hadith_by_reference', Mock(return_value=None))
    assert client.get('/hadith/missing').status_code == 404
    monkeypatch.setattr(user_routes, 'get_hadith_by_mode', Mock(side_effect=ValueError('bad data')))
    response = client.get('/api/fetch-hadith?fetch-mode=daily')
    assert response.status_code == 400
    assert response.json == {'error': 'Something went wrong'}
