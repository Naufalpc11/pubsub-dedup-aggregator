from pathlib import Path
import time

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.queue import event_queue
from src.services.stats import reset_stats
from src.storage import db


def _drain_queue():
    while True:
        try:
            event_queue.get_nowait()
            event_queue.task_done()
        except Exception:
            break


@pytest.fixture(autouse=True)
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    test_db = tmp_path / "events_test.db"
    monkeypatch.setattr(db, "DB_PATH", str(test_db))
    db.init_db()
    reset_stats()
    _drain_queue()
    yield
    _drain_queue()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


def wait_until(assertion_fn, timeout: float = 3.0, interval: float = 0.05):
    deadline = time.time() + timeout
    last_error = None

    while time.time() < deadline:
        try:
            assertion_fn()
            return
        except AssertionError as err:
            last_error = err
            time.sleep(interval)

    if last_error is not None:
        raise last_error


@pytest.fixture
def wait_until_fn():
    return wait_until
