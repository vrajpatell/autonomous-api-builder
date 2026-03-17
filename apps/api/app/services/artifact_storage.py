from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from app.core.config import settings


@dataclass
class StoredArtifact:
    backend: str
    key: str
    size_bytes: int


class ArtifactStorageBackend(Protocol):
    backend_type: str

    def save_bytes(self, *, task_id: int, artifact_type: str, file_name: str, content: bytes) -> StoredArtifact:
        ...

    def read_bytes(self, key: str) -> bytes:
        ...


class LocalArtifactStorage:
    backend_type = "local"

    def __init__(self, base_path: str) -> None:
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, *, task_id: int, artifact_type: str, file_name: str, content: bytes) -> StoredArtifact:
        safe_artifact_type = self._sanitize_segment(artifact_type)
        safe_file_name = self._sanitize_filename(file_name)
        unique_prefix = uuid4().hex
        relative_key = Path("tasks") / str(task_id) / safe_artifact_type / f"{unique_prefix}-{safe_file_name}"
        output_path = self.base_path / relative_key
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(content)
        return StoredArtifact(backend=self.backend_type, key=relative_key.as_posix(), size_bytes=len(content))

    def read_bytes(self, key: str) -> bytes:
        resolved = (self.base_path / key).resolve()
        if self.base_path not in resolved.parents and resolved != self.base_path:
            raise ValueError("Invalid artifact key")
        return resolved.read_bytes()

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        stripped = name.strip().replace("\\", "-").replace("/", "-")
        return stripped or "artifact.bin"

    @staticmethod
    def _sanitize_segment(value: str) -> str:
        return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value).strip("-") or "artifact"


class ArtifactStorageService:
    def __init__(self, backend: ArtifactStorageBackend):
        self.backend = backend

    def save_text(
        self,
        *,
        task_id: int,
        artifact_type: str,
        file_name: str,
        content: str,
        encoding: str = "utf-8",
    ) -> StoredArtifact:
        return self.backend.save_bytes(
            task_id=task_id,
            artifact_type=artifact_type,
            file_name=file_name,
            content=content.encode(encoding),
        )

    def save_bytes(self, *, task_id: int, artifact_type: str, file_name: str, content: bytes) -> StoredArtifact:
        return self.backend.save_bytes(task_id=task_id, artifact_type=artifact_type, file_name=file_name, content=content)

    def read_bytes(self, key: str) -> bytes:
        return self.backend.read_bytes(key)


def get_artifact_storage() -> ArtifactStorageService:
    backend = settings.storage_backend.lower()
    if backend == "local":
        return ArtifactStorageService(LocalArtifactStorage(settings.storage_local_base_path))
    raise ValueError(f"Unsupported storage backend: {backend}")
