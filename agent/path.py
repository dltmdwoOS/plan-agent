import os
from pathlib import Path

LOCALE = os.getenv("LOCALE")
BASE_DIR   = Path(__file__).resolve().parent
MEMORY_DIR = BASE_DIR / 'memory'
IMAGE_DIR  = MEMORY_DIR / 'image'

LOCALE_DIR = BASE_DIR / 'locale' / LOCALE
PROMPT_DIR = LOCALE_DIR / 'prompts'
DESC_DIR   = LOCALE_DIR / 'descriptions'

LOCALE_DIR.mkdir(parents=True, exist_ok=True)
PROMPT_DIR.mkdir(parents=True, exist_ok=True)
DESC_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)