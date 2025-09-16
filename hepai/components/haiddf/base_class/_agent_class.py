
from dataclasses import dataclass, field
from typing import Dict, Union, Literal


@dataclass
class AgentInfo:
    id: str = field(default=None, metadata={"help": "Agent's ID"})
    object: str = field(default="agent", metadata={"help": "Object type"})
    owner: str = field(default=None, metadata={"help": "Owner of the agent"})
    description: str = field(default=None, metadata={"help": "Description of the agent"})
    version: str = field(default="1.0", metadata={"help": "Version of the agent"})