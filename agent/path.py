from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent
PROMPT_DIR = BASE_DIR / 'prompts'
MEMORY_DIR = BASE_DIR / 'memory'
DESC_DIR   = BASE_DIR / 'descriptions'
IMAGE_DIR  = MEMORY_DIR / 'image'

PROMPT_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
DESC_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)