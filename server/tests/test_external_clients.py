import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
import requests

from hadith_app.client import hadith_api_client
from hadith_app.service import explanation_store, hadith_service


@pytest.fixture(params=['web', 'script'])
def explanation_consumer(request):
    if request.param == 'web':
        return explanation_store
    path = Path(__file__).resolve().parents[2] / 'scripts/store_ai_hadith_explanation_in_db.py'
    spec = importlib.util.spec_from_file_location('explanation_script', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def response(content='{"en":"Explanation", "ar":"تفسير"}', refusal=None, finish_reason='stop'):
    return SimpleNamespace(choices=[SimpleNamespace(
        finish_reason=finish_reason, message=SimpleNamespace(content=content, refusal=refusal))])


@pytest.mark.parametrize('result', [None, SimpleNamespace(choices=[]), response(None), response('invalid'),
    response('[]'), response('{"en":42,"ar":"تفسير"}'), response('{"en":"only"}'),
    response(refusal='refused'), response(finish_reason='length')])
def test_unusable_explanation_returns_none(explanation_consumer, monkeypatch, result):
    client = Mock()
    client.chat.completions.create.return_value = result
    monkeypatch.setattr(explanation_consumer, 'client', client)
    assert explanation_consumer.fetch_hadith_explanation('حديث') is None


@pytest.mark.parametrize('error', [RuntimeError('API failure'), httpx.ReadTimeout('timeout')])
def test_explanation_failure_returns_none(explanation_consumer, monkeypatch, error):
    client = Mock()
    client.chat.completions.create.side_effect = error
    monkeypatch.setattr(explanation_consumer, 'client', client)
    assert explanation_consumer.fetch_hadith_explanation('حديث') is None


@pytest.mark.parametrize('text', [None, '', '   '])
def test_empty_explanation_input_skips_api(explanation_consumer, monkeypatch, text):
    client = Mock()
    monkeypatch.setattr(explanation_consumer, 'client', client)
    assert explanation_consumer.fetch_hadith_explanation(text) is None
    client.chat.completions.create.assert_not_called()


def test_explanation_schema_and_model_preserved(explanation_consumer, monkeypatch):
    client = Mock()
    client.chat.completions.create.return_value = response()
    monkeypatch.setattr(explanation_consumer, 'client', client)
    assert explanation_consumer.fetch_hadith_explanation('حديث') == {'en': 'Explanation', 'ar': 'تفسير'}
    args = client.chat.completions.create.call_args.kwargs
    assert args['model'] == 'gpt-4o-mini'
    assert args['response_format']['json_schema']['strict'] is True
    assert set(args['response_format']['json_schema']['schema']['required']) == {'en', 'ar'}


def test_failed_explanation_does_not_update_database(monkeypatch):
    monkeypatch.setattr(hadith_service, 'fetch_hadith_content', Mock(return_value='حديث'))
    monkeypatch.setattr(explanation_store, 'fetch_hadith_explanation', Mock(return_value=None))
    update = Mock()
    monkeypatch.setattr(hadith_service.hadith_dao, 'update_hadith_explanation', update)
    assert hadith_service.generate_new_hadith_explanation('fixture-ref') is None
    update.assert_not_called()


@pytest.mark.parametrize('error', [requests.Timeout('timeout'), requests.HTTPError('bad status'), requests.exceptions.JSONDecodeError('invalid', '', 0)])
def test_hadith_client_handles_request_errors(monkeypatch, error):
    get = Mock(side_effect=error)
    monkeypatch.setattr(hadith_api_client.requests, 'get', get)
    assert hadith_api_client.fetch_hadith('book', 1, 1) is None
    assert get.call_args.kwargs['timeout'] == (5, 30)


@pytest.mark.parametrize('data,expected', [({'hadiths': {'data': []}}, {}), ({'hadiths': {'data': [{'id': 1}]}}, {'id': 1}), ({}, None)])
def test_hadith_client_responses(monkeypatch, data, expected):
    api_response = Mock()
    api_response.json.return_value = data
    monkeypatch.setattr(hadith_api_client.requests, 'get', Mock(return_value=api_response))
    assert hadith_api_client.fetch_hadith('book', 1, 1) == expected
    api_response.raise_for_status.assert_called_once()
