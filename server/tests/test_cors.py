from unittest.mock import Mock

import pytest

from hadith_app.service import user_service

ORIGINS = [
    'https://example.org',
    'chrome-extension://jgofbnjkimhpkjeimcedipdeecegdkpp',
    'moz-extension://test-installation-id',
]


@pytest.mark.parametrize('origin', ORIGINS)
@pytest.mark.parametrize('path,method', [('/api/fetch-hadith', 'GET'), ('/auth/api/get-token', 'POST'), ('/admin/api/delete-today-hadith', 'GET')])
def test_authorization_preflight(client, origin, path, method):
    response = client.options(path, headers={
        'Origin': origin,
        'Access-Control-Request-Method': method,
        'Access-Control-Request-Headers': 'Authorization, Content-Type',
        'Access-Control-Request-Private-Network': 'true',
    })
    assert response.status_code == 200
    assert response.headers['Access-Control-Allow-Origin'] == origin
    assert 'authorization' in response.headers['Access-Control-Allow-Headers'].lower()
    assert method in response.headers['Access-Control-Allow-Methods']
    assert response.headers.get('Access-Control-Allow-Private-Network', '').lower() != 'true'
    assert 'Access-Control-Allow-Credentials' not in response.headers


@pytest.mark.parametrize('origin', ORIGINS)
def test_cors_on_success_and_errors(client, hadith_fixture, monkeypatch, origin):
    monkeypatch.setattr(user_service, 'fetch_user_by_username', Mock(return_value=None))
    for path, status in [('/api/fetch-hadith?fetch-mode=daily', 200),
                         ('/api/fetch-hadith', 400),
                         ('/admin/api/delete-today-hadith', 401)]:
        response = client.get(path, headers={'Origin': origin})
        assert response.status_code == status
        assert response.headers['Access-Control-Allow-Origin'] == origin
    response = client.post('/auth/api/get-token', data={}, headers={'Origin': origin})
    assert response.status_code == 401
    assert response.headers['Access-Control-Allow-Origin'] == origin


def test_cors_on_rate_limit_error(client, hadith_fixture):
    headers = {'Origin': ORIGINS[0]}
    responses = [client.get('/api/today-hadith', headers=headers) for _ in range(4)]
    assert responses[-1].status_code == 429
    assert responses[-1].headers['Access-Control-Allow-Origin'] == ORIGINS[0]


def test_request_without_origin(client, hadith_fixture):
    assert client.get('/api/today-hadith').status_code == 200
