import json
from logging import getLogger
from pathlib import Path
from typing import Any, Iterable, Optional

from httpx import Client, Headers, QueryParams, Response

from .constants import BASE_API_URL
from .models import Collection, Project, Version

type ModrinthModel = Collection | Project | Version

logger = getLogger("ModrinthApi")


class ModrinthException(Exception): ...


class ModrinthApi:
    def __init__(
        self,
        token: str,
        game_version: str,
        game_loader: str,
        *,
        chunk_size: int = 100,
        cache_file: str = "versions.cache",
    ) -> None:
        self.game_version = game_version
        self.game_loader = game_loader
        self.token = token
        self.chunk_size = chunk_size
        self.cache_file = Path(cache_file)

        if not self._is_valid("tag/game_version", self.game_version, "version"):
            raise ValueError("Game version is not valid")

        if not self._is_valid("tag/loader", self.game_loader, "name"):
            raise ValueError("Loader is not valid")

    def _send_request(
        self,
        endpoint: str,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        *,
        use_v3: bool = False,
    ) -> Response:
        _headers: Headers = {"Authorization": self.token, **(headers or {})}
        _params: QueryParams = {
            key: (json.dumps(value) if isinstance(value, list) else value)
            for key, value in (params or {}).items()
        }
        url = f"{BASE_API_URL}/v{3 if use_v3 else 2}/{endpoint}"

        with Client(timeout=10.0) as client:
            response = client.get(url, headers=_headers, params=_params)
            response.raise_for_status()

        return response

    def _is_valid(self, endpoint: str, value: str, key: str) -> bool:
        response = self._send_request(endpoint)
        response_dict: list[dict[str, Any]] = response.json()

        for item in response_dict:
            if item[key] == value:
                return True

        return False

    def _make_chunks(self, data: Iterable[str]) -> tuple[Iterable[str], ...]:
        if len(data) <= self.chunk_size:
            return tuple([data])

        logger.debug("Split data to chunks (%i per chunk)", self.chunk_size)
        chunks = tuple(data[i : i + self.chunk_size] for i in range(0, len(data), self.chunk_size))
        logger.debug("Total number of chunks: %i", len(chunks))

        return chunks

    def _save_versions_to_cache(
        self, project_id: str, raw_versions: Iterable[dict[str, Any]]
    ) -> None:
        self.cache_file.touch()
        cache: dict[str, dict[str, dict[str, Any]]] = json.loads(self.cache_file.read_text() or "{}")
        cache[project_id] = {
            **cache.get(project_id, {}),
            **{version["id"]: version for version in raw_versions},
        }
        self.cache_file.write_text(json.dumps(cache))

    def _get_versions_from_cache(
        self, project_id: str, version_ids: Iterable[str]
    ) -> tuple[list[Version], tuple[str, ...]]:
        cache: dict[str, dict[str, dict[str, Any]]] = json.loads(self.cache_file.read_text() or "{}")
        project_versions = cache.get(project_id)

        if not project_versions:
            return [], version_ids

        versions = []
        missing_ids = list(version_ids)
        for version_id, raw_version in project_versions.items():
            if version_id in version_ids:
                missing_ids.remove(version_id)
                if (
                    self.game_loader in raw_version["loaders"]
                    and self.game_version in raw_version["game_versions"]
                ):
                    versions.append(Version.from_dict(raw_version))
                

        return versions, tuple(missing_ids)

    def get_project(self, project_id: str) -> Optional[Project]:
        response = self._send_request(f"project/{project_id}")
        project = Project.from_dict(response.json())
        logger.info("Project fetched: '%s'", project.name)

        if (
            self.game_loader not in project.loaders
            or self.game_version not in project.game_versions
        ):
            logger.warning("The project does not match the game loader or game version.")
            return None

        logger.debug("- Modrinth URL: %s", project.modrinth_url)
        logger.debug("- Versions: %i", len(project.version_ids))

        return project

    def get_project_versions(self, project: Project) -> tuple[Version, ...]:
        versions, version_ids = self._get_versions_from_cache(project.id, project.version_ids)
        chunks = self._make_chunks(version_ids)

        if len(version_ids) > 0:
            for number, ids in enumerate(chunks):
                if len(chunks) > 1:
                    logger.debug("- Chunk %i", number)

                response = self._send_request("versions", {"ids": list(ids)})
                self._save_versions_to_cache(project.id, response.json())
                versions.extend(
                    [
                        Version.from_dict(data)
                        for data in response.json()
                        if self.game_loader in data["loaders"]
                        and self.game_version in data["game_versions"]
                    ]
                )

        logger.info("Fetched versions: %i", len(version_ids))
        logger.debug("- Matched versions %i", len(versions))

        return tuple(versions)

    def get_version(self, version_id: str) -> Version:
        logger.info("Fetching version: '%s' ", version_id)
        response = self._send_request(f"version/{version_id}")
        version = Version.from_dict(response.json())

        logger.info("Version fetched")

        return version

    def get_collection(self, collection_id: str) -> Collection:
        response = self._send_request(f"collection/{collection_id}", use_v3=True)
        collection = Collection.from_dict(response.json())

        logger.info("Collection fetched: %s", collection.name)
        logger.debug("- Modrinth URL: %s", collection.modrinth_url)
        logger.debug("- Projects: %i", len(collection.project_ids))

        return collection
