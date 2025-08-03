from dataclasses import dataclass
from pathlib import Path

@dataclass
class ChainConfig:
    name: str
    yaml: Path
    model_family: str = "openai"
    model_name: str  = "gpt-4o-mini"