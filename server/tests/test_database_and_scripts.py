import importlib.util
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock

import pytest

from hadith_app.db import db_utils
from hadith_app.dao.hadith_dao import bind_to_hadith_meta


def load_script(name):
    path = Path(__file__).resolve().parents[2] / f'scripts/{name}.py'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sqlite_reads_writes_and_cleanup(tmp_path, monkeypatch):
    monkeypatch.setattr(db_utils, 'DATABASE_URL', f'sqlite:///{tmp_path / "test.db"}')
    db = db_utils.Database()
    db.connect()
    try:
        db.execute_modify_query('CREATE TABLE fixture (value TEXT)')
        assert db.execute_modify_query('INSERT INTO fixture VALUES (?)', ('حديث',)) == 1
        assert db.execute_read_query('SELECT value FROM fixture WHERE value=?', ('حديث',)) == [('حديث',)]
        with pytest.raises(sqlite3.OperationalError):
            db.execute_read_query('SELECT missing FROM fixture')
    finally:
        db.close_connection()
    assert db.conn is None
    # Confirm writes survive a new connection.
    db.connect()
    assert db.execute_read_query('SELECT value FROM fixture') == [('حديث',)]
    db.close_connection()


def test_postgres_placeholders_and_binary_explanations(monkeypatch):
    monkeypatch.setattr(db_utils, 'DATABASE_URL', 'postgresql://disposable-test')
    connection = Mock()
    monkeypatch.setattr(db_utils.psycopg2, 'connect', Mock(return_value=connection))
    db = db_utils.Database()
    db.connect()
    db.execute_modify_query('UPDATE fixture SET value=? WHERE id=?', ('حديث', 1))
    connection.cursor.return_value.execute.assert_called_once_with('UPDATE fixture SET value=%s WHERE id=%s', ('حديث', 1))
    connection.commit.assert_called_once()
    db.close_connection()
    connection.close.assert_called_once()
    meta = bind_to_hadith_meta(('ref', json.dumps({'hadithArabic': 'حديث'}).encode(), memoryview('تفسير'.encode()), b'Explanation'))
    assert meta.ar_explanation == 'تفسير'
    assert meta.en_explanation == 'Explanation'


def test_csv_import_uses_disposable_database(tmp_path, monkeypatch):
    pytest.importorskip('pandas', reason='Install scripts/requirements.lock to check the CSV importer')
    module = load_script('setup_hadith_db')
    fixture = tmp_path / 'fixture.csv'
    fixture.write_text('reference,book,chapter,hadithnumber,notes\nREF1,book,1,2,\nREF2,book,3,4,حديث\n')
    monkeypatch.chdir(tmp_path)
    module.load_db(fixture)
    with sqlite3.connect(tmp_path / 'app.db') as conn:
        assert conn.execute('SELECT * FROM hadith_meta ORDER BY reference').fetchall() == [
            ('REF1', 'book', 1, 2, None), ('REF2', 'book', 3, 4, 'حديث')]
        assert [row[2] for row in conn.execute('PRAGMA table_info(hadith_meta)')] == ['TEXT', 'TEXT', 'INTEGER', 'INTEGER', 'TEXT']


def test_failed_script_explanation_does_not_insert(monkeypatch):
    module = load_script('store_ai_hadith_explanation_in_db')
    connection = Mock()
    monkeypatch.setattr(module.psycopg2, 'connect', Mock(return_value=connection))
    monkeypatch.setattr(module, 'fetch_hadith_explanation', Mock(return_value=None))
    module._do_process('postgresql://disposable-test', [('ref', b'{"hadithArabic":"fixture"}')])
    connection.cursor.return_value.execute.assert_not_called()
    connection.close.assert_called_once()


@pytest.mark.parametrize('error', [None, 'timeout', 'json', 'http'])
def test_crawler_timeout_and_request_errors(monkeypatch, error):
    import requests
    module = load_script('hadiths_crawler')
    response = Mock()
    response.json.return_value = {'hadiths': {'data': [{'id': 1}]}}
    get = Mock(return_value=response)
    if error:
        get.side_effect = {'timeout': requests.Timeout(), 'json': requests.exceptions.JSONDecodeError('bad', '', 0), 'http': requests.HTTPError()}[error]
    monkeypatch.setattr(module.requests, 'get', get)
    assert module.fetch_hadiths('book', 1, 'Sahih') == ([] if error else [{'id': 1}])
    assert get.call_args.kwargs['timeout'] == (5, 30)


def test_postgres_integration(monkeypatch):
    import os
    url = os.getenv('TEST_POSTGRES_URL')
    if not url:
        pytest.skip('Set TEST_POSTGRES_URL to a disposable PostgreSQL database')
    monkeypatch.setattr(db_utils, 'DATABASE_URL', url)
    db = db_utils.Database()
    db.connect()
    try:
        db.execute_modify_query('CREATE TEMP TABLE upgrade_fixture (id INTEGER, value BYTEA)')
        db.execute_modify_query('INSERT INTO upgrade_fixture VALUES (?, ?)', (1, 'تفسير'.encode()))
        rows = db.execute_read_query('SELECT value FROM upgrade_fixture WHERE id=?', (1,))
        assert bytes(rows[0][0]).decode() == 'تفسير'
        with pytest.raises(db_utils.psycopg2.Error):
            db.execute_read_query('SELECT missing FROM upgrade_fixture')
        db.conn.rollback()
        assert db.execute_read_query('SELECT count(*) FROM upgrade_fixture') == [(1,)]
    finally:
        db.close_connection()
    assert db.conn is None
