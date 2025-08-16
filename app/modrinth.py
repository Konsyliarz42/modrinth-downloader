from pathlib import Path
from typing import Any, Final, cast
from urllib.request import Request, urlopen

import tomllib
from bs4 import BeautifulSoup, Tag
from httpx import Client, Headers, Response

from .models import Collection, Project, Version

BASE_API_URL: Final[str] = "https://api.modrinth.com/v2"
BASE_URL: Final[str] = "https://modrinth.com"
REQUEST_TIMEOUT: Final[float] = 10.0


class ModrinthApi:
    def __init__(
        self, game_version: str, game_loaders: list[str], token: str | None = None
    ) -> None:
        self.game_version = game_version
        self.game_loaders = game_loaders
        self.token = token

        self.game_versions = [game_version]
        if (game_version.count(".") == 2):
            version, _ = game_version.rsplit(".", 1)
            self.game_versions.append(version)
        

    def _build_user_agent(self) -> str:
        pyproject = tomllib.loads(Path("pyproject.toml").read_text())["tool"]["poetry"]
        return f"Konsyliarz42/{pyproject['name']}/{pyproject['version']}"

    def _build_url(
        self,
        endpoint: str,
        query_params: dict[str, Any | list[Any]] | None = None,
    ) -> str:
        def list_to_query_param(data: list[Any]) -> str:
            if len(data) == 0:
                return ""

            if isinstance(data[0], str):
                return f"[{', '.join([f'"{d}"' for d in data])}]"

            return f"[{', '.join(data)}]"

        if endpoint.startswith("/"):
            raise ValueError("Endpoint cannot start with `/`")

        query = ""

        if query_params:
            query += "?"
            query_items: list[str] = []
            for [key, value] in query_params.items():
                parsed_value = value if not isinstance(value, list) else list_to_query_param(value)  # type: ignore
                query_items.append(f"{key}={parsed_value}")
            query += "&".join(query_items)

        return f"{BASE_API_URL}/{endpoint}{query}"

    def _send_request(
        self,
        url: str,
        headers: Headers | None = None,
    ) -> Response:
        _headers = (
            Headers({"Authorization": self.token or "", "User-Agent": self._build_user_agent()})
            if not headers
            else headers
        )

        with Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(
                url=url,
                headers=_headers,
            )
            response.raise_for_status()

        return response

    def read_projects(self, ids: list[str]) -> list[Project]:
        url = self._build_url("projects", {"ids": ids})
        response = self._send_request(url)

        return sorted(
            [Project(**project) for project in response.json()],
            key=lambda p: p.title,
        )

    def read_project_versions(self, id: str) -> list[Version]:
        url = self._build_url(
            f"project/{id}/version",
            {
                "loaders": self.game_loaders,
                "game_versions": self.game_versions,
            },
        )
        response = self._send_request(url)

        return sorted(
            [Version(**version) for version in response.json()],
            key=lambda v: v.date_published,
            reverse=True,
        )

    def read_collection(
        self, id: str
    ) -> Collection | None:  # Labyrinth does not yet support collections
        url = f"{BASE_URL}/collection/{id}"
        request = Request(url, headers={"User-Agent": self._build_user_agent()})  # noqa: S310
        page = urlopen(request)  # noqa: S310
        soup = BeautifulSoup(page, "html.parser")

        h1 = cast(Tag | None, soup.find("h1", attrs={"class": "title"}))
        if not h1:
            return None

        project_ids: list[str] = []
        for _article in soup.find_all("article", attrs={"class": "project-card"}):
            article = cast(Tag | None, _article)
            if not article:
                continue

            a = cast(Tag | None, article.find("a"))
            if not a:
                continue

            href = cast(str | None, a.attrs.get("href"))
            if not href:
                continue

            _, project_id = href.rsplit("/", 1)
            project_ids.append(project_id)

        return Collection(id=id, projects=project_ids, title=h1.text)
