from dataclasses import dataclass


@dataclass
class Project:
    id: str
    name: str
    type: str
    slug: str

    def __repr__(self) -> str:
        return f"<Project: {self.id} | {self.type} | {self.name}>"

    @classmethod
    def from_json(csl, data: dict) -> "Project":
        return Project(
            id=data["id"],
            name=data["title"],
            type=data["project_type"],
            slug=data["slug"],
        )


@dataclass
class Version:
    id: str
    number: str
    required_versions: list[str]
    required_projects: list[str]
    file_size: int
    file_name: str
    file_url: str

    def __repr__(self) -> str:
        return f"<Version: {self.id} | {self.number}>"

    @classmethod
    def from_json(csl, data: dict) -> "Version":
        file = data["files"][0]
        dependencies = [
            (dep["version_id"], dep["project_id"])
            for dep in data["dependencies"]
            if dep["dependency_type"] == "required"
        ]
        required_versions = []
        required_projects = []

        for version_id, project_id in dependencies:
            if version_id:
                required_versions.append(version_id)
            else:
                required_projects.append(project_id)

        return Version(
            id=data["id"],
            number=data["version_number"],
            required_versions=required_versions,
            required_projects=required_projects,
            file_size=file["size"],
            file_name=file["filename"],
            file_url=file["url"],
        )
