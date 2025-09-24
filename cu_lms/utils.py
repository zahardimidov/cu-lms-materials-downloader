import re
from pathlib import Path

_EMOJI_RE = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # emoticons
    "\U0001f300-\U0001f5ff"  # symbols & pictographs
    "\U0001f680-\U0001f6ff"  # transport & map symbols
    "\U0001f1e0-\U0001f1ff"  # flags
    "\U00002702-\U000027b0"
    "\U000024c2-\U0001f251"
    "]+",
    flags=re.UNICODE,
)

_BAD_FS_CHARS = r'[\\/*?"<>|]+'


def _clean_segment(txt: str) -> str:
    """Вспомогательная чистка от эмодзи, запрещённых символов и лишних пробелов."""
    txt = _EMOJI_RE.sub("", txt).strip()
    txt = re.sub(_BAD_FS_CHARS, " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt or "untitled"


def sanitize_title(name: str) -> str:
    """Для названий курсов/недель (обрезка по .,: и чистка символов)."""
    if not name:
        return "untitled"
    txt = _EMOJI_RE.sub("", name).strip()
    for ch in ".,:":
        if ch in txt:
            txt = txt.split(ch, 1)[0].strip()
    return _clean_segment(txt)


def sanitize_filename(name: str) -> str:
    """Для файлов: сохраняет расширение, чистит только имя."""
    if not name:
        return "file"

    p = Path(name).name

    suffixes = "".join(Path(p).suffixes)
    stem = p[: len(p) - len(suffixes)] if suffixes else p

    clean_stem = _clean_segment(stem)
    clean_suffixes = re.sub(r"\s", "", suffixes)

    return (clean_stem or "file") + clean_suffixes


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
