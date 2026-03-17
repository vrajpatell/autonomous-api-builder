import os
import shutil
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["QUEUE_BACKEND"] = "noop"
os.environ["STORAGE_BACKEND"] = "local"
os.environ["STORAGE_LOCAL_BASE_PATH"] = "./test-artifacts"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.main import app
from app.models.base import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    artifact_dir = Path("./test-artifacts")
    if artifact_dir.exists():
        shutil.rmtree(artifact_dir)
    yield
    Base.metadata.drop_all(bind=engine)
    if artifact_dir.exists():
        shutil.rmtree(artifact_dir)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
