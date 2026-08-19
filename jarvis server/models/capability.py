from dataclasses import dataclass
from typing import Any


@dataclass
class Parameter:
    name: str
    type: str
    description: str
    required: bool
    default: Any = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
            "default": self.default,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Parameter":
        return cls(
            name=data["name"],
            type=data["type"],
            description=data["description"],
            required=data["required"],
            default=data.get("default"),
        )


@dataclass
class Capability:
    name: str
    description: str
    parameters: list[Parameter]

    requires_online: bool = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                parameter.to_dict() for parameter in self.parameters
            ],
            "requires_online": self.requires_online,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Capability":
        return cls(
            name=data["name"],
            description=data["description"],
            parameters=[
                Parameter.from_dict(parameter) for parameter in data["parameters"]
            ],
            requires_online=data.get("requires_online", True),
        )