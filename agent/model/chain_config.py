from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class ChainConfig:
    name: str
    yaml: Optional[Path]
    model_family: str = "openai"
    model_name: str  = "gpt-4o-mini"