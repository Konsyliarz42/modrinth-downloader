from dataclasses import dataclass
from typing import Optional


@dataclass
class Mod:
    id_or_slug: str
    version_id: Optional[str]

    @classmethod
    def from_json(csl, data: dict) -> "Mod":
        return Mod(
            id_or_slug=data["id_or_slug"],
            version_id=data.get("version_id"),
        )
