import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("search_path", [".", "hadith_app"])
def test_direct_script_starts_registered_application(search_path):
    server_dir = Path(__file__).resolve().parents[1]
    # Model Python's script search path, without relying on a caller's PYTHONPATH.
    code = '''
import runpy
import sys
from unittest.mock import patch
from flask import Flask

sys.path[0] = SEARCH_PATH
with patch.object(Flask, 'run', autospec=True) as run:
    runpy.run_path('hadith_app/app.py', run_name='__main__')
    from hadith_app import app
    from flask_limiter import RateLimitExceeded
    run.assert_called_once_with(app)
    assert app.error_handler_spec[None][429][RateLimitExceeded].__name__ == 'ratelimit_handler'
    assert any(fn.__name__ == 'close_db' for fn in app.teardown_appcontext_funcs)
    assert any(rule.rule == '/api/today-hadith' for rule in app.url_map.iter_rules())
'''
    code = code.replace('SEARCH_PATH', repr(search_path))
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    result = subprocess.run([sys.executable, '-c', code], cwd=server_dir,
                            env=env, text=True, capture_output=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
