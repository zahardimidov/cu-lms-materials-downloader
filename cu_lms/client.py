import json
from pathlib import Path
from typing import Callable, List, Optional

import requests
from .config import Settings
from .exceptions import UnauthorizedError, ApiError, NotFoundError
from .models import Course, Week, FileModel
from .utils import sanitize_filename, sanitize_title, ensure_dir


class LMSClient:
    """HTTP-клиент для API Central University."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self._session = requests.Session()
        self._session.headers.update(self._load_headers(self.settings.headers_path))

    def _load_headers(self, path: Path) -> dict:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _get(self, path: str, params: dict | None = None) -> requests.Response:
        url = self.settings.base_url + path
        resp = self._session.get(url, params=params, timeout=self.settings.timeout)
        if resp.status_code == 401:
            raise UnauthorizedError(
                "Попробуйте указать корректный Cookie в headers.json"
            )
        if resp.status_code == 404:
            raise NotFoundError(f"Ресурс не найден: {path}")
        if not resp.ok:
            raise ApiError(f"Ошибка API {resp.status_code}: {resp.text[:200]}")
        return resp

    def get_courses(
        self, predicate: Optional[Callable[[Course], bool]] = None
    ) -> List[Course]:
        resp = self._get("/api/micro-lms/courses/student?limit=10000&state=published")
        items = resp.json().get("items", [])
        courses = [Course(**i) for i in items]
        return list(filter(predicate, courses)) if predicate else courses

    def get_course_weeks(
        self, course_id: int, predicate: Optional[Callable[[Week], bool]] = None
    ) -> List[Week]:
        resp = self._get(f"/api/micro-lms/courses/{course_id}/overview")
        themes = resp.json().get("themes", [])
        weeks = [
            Week(**t)
            for t in themes
            if isinstance(t, dict)
            and ("Неделя" in t.get("name", "") or "Week" in t.get("name", ""))
        ]
        return list(filter(predicate, weeks)) if predicate else weeks

    def get_course_week(self, course_id: int, week_number: int) -> Week:
        weeks = self.get_course_weeks(course_id)
        if week_number < 1 or week_number > len(weeks):
            raise NotFoundError(
                f"Неделя #{week_number} не найдена (доступно: 1..{len(weeks)})"
            )
        return weeks[week_number - 1]

    def get_course_materials(self, section_id: int) -> List[FileModel]:
        resp = self._get(f"/api/micro-lms/longreads/{section_id}/materials?limit=10000")
        items = resp.json().get("items", [])
        return [
            FileModel(**f)
            for f in items
            if isinstance(f, dict) and f.get("discriminator") == "file"
        ]

    def download_course_file(self, filename: str, version: str, filepath: Path) -> bool:
        params = {"filename": filename, "version": version}
        resp = self._get("/api/micro-lms/content/download-link", params=params)
        data = resp.json()
        url = data.get("url")
        if not url:
            return False

        r = self._session.get(url, timeout=self.settings.timeout)
        if not r.ok or len(r.content) <= 1_000:
            return False

        ensure_dir(filepath.parent)
        with filepath.open("wb") as f:
            f.write(r.content)
        return True

    def download_week_files(
        self, course: Course, week: Week, out_dir: Path
    ) -> list[Path]:
        saved: list[Path] = []
        base = ensure_dir(
            out_dir / sanitize_title(course.name) / sanitize_title(week.name)
        )
        for section in week.sections:
            for file in self.get_course_materials(section.id):
                fname = sanitize_filename(file.filename)
                target = base / fname
                ok = self.download_course_file(file.filename, file.version, target)
                if ok:
                    saved.append(target)
        return saved
