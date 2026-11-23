from collections.abc import Iterator

import pytest

from app import database


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch) -> Iterator[None]:
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    yield
