"""Configuration."""

from dataclasses import dataclass, field

from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class Config(YamlDataClassConfig):
    """Configuration."""

    # Reason: To use auto complete
    area_id: str = "JP13"
    number_process: int = 3
    stop_if_file_exists: bool = False
    keywords: list[str] = field(default_factory=list)
