import os
from datetime import datetime
from typing import Optional

import httpx

from .models import Project, Version
from .utils import build_url


class ModrinthError(Exception):
    pass


class ModrinthAPI:
    def __init__(self, personal_access_token: str, project_version: str) -> None:
        self.token = personal_access_token
        self.project_version = project_version

    def _send_request(
        self,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> httpx.Response:
        url = build_url("https://api.modrinth.com/v2", endpoint, params)
        headers = {
            "Authorization": self.token,
            "User-Agent": (
                "https://github.com/Konsyliarz42/modrinth-downloader/tree/"
                f"{self.project_version}"
            ),
            "Content-Type": "application/json",
        }

        with httpx.Client() as client:
            response = client.get(url, headers=headers)

        response.raise_for_status()

        return response

    def get_project(self, id_or_slug: str) -> Project:
        endpoint = f"/project/{id_or_slug}"
        response = self._send_request(endpoint)
        response_json = response.json()

        if not response_json:
            raise ModrinthError("Project not found")

        project = Project.from_json(response_json)

        return project

    def get_all_versions(self, project_id_or_slug: str) -> list[Version]:
        endpoint = f"/project/{project_id_or_slug}/version"
        params = {
            "loaders": [os.environ["MOD_LOADER"]],
            "game_versions": [os.environ["GAME_VERSION"]],
        }
        response = self._send_request(endpoint, params)
        response_json = response.json()

        if not response_json:
            raise ModrinthError("Versions not found")

        sorted_response_json = sorted(
            response_json,
            reverse=True,
            key=lambda data: datetime.fromisoformat(data["date_published"]),
        )

        return [Version.from_json(data) for data in sorted_response_json]

    def get_version(self, version_id: str) -> Version:
        endpoint = f"/version/{version_id}"
        response = self._send_request(endpoint)
        response_json = response.json()

        if not response_json:
            raise ModrinthError("Version not found")

        version = Version.from_json(response_json)

        return version
