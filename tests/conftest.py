import os
import tempfile
from pathlib import Path

_TEST_DB_DIR = tempfile.TemporaryDirectory(prefix="lab7-tests-")

os.environ["DATABASE"] = str(
    Path(_TEST_DB_DIR.name) / "test.sqlite"
)

import pytest
import models
from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)

    db_path = Path(flask_app.config["DATABASE"])

    db_path.unlink(missing_ok=True)

    with flask_app.app_context():
        models.init_db()

    yield flask_app

    with flask_app.app_context():
        models.close_db()


@pytest.fixture
def client(app):
    return app.test_client()
