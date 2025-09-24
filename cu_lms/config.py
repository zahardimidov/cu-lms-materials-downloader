from dataclasses import dataclass
from pathlib import Path
import os

DEFAULT_BASE_URL = "https://my.centraluniversity.ru"
DEFAULT_HEADERS_PATH = Path("headers.json")
DEFAULT_TIMEOUT = (5, 30)

DEFAULT_DOWNLOAD_ROOT = Path(os.getenv("DOWNLOAD_ROOT", "./downloads")).resolve()


@dataclass
class Settings:
    base_url: str = DEFAULT_BASE_URL
    headers_path: Path = DEFAULT_HEADERS_PATH
    timeout: tuple[int, int] = DEFAULT_TIMEOUT
    download_root: Path = DEFAULT_DOWNLOAD_ROOT
