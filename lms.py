import json
import re

import requests
from pydantic import BaseModel, Field


class Parent(BaseModel):
    @property
    def path(self):
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "]+",
            flags=re.UNICODE,
        )
        txt = emoji_pattern.sub(r"", self.name).strip()

        for i in ".,:":
            txt = txt.split(i)[0].strip()
        return txt


class Course(Parent):
    id: int
    name: str
    state: str
    isArchived: bool


class Section(Parent):
    id: int
    type: str
    name: str


class Week(Parent):
    id: int
    name: str
    sections: list[Section] = Field(..., alias="longreads")


class File(BaseModel):
    discriminator: str
    viewType: str
    mediaType: str
    filename: str
    version: str
    length: int


class LMS:
    def __init__(self):
        self.base_url = "https://my.centraluniversity.ru"

    def get(self, path, params=None):
        headers = json.load(open("headers.json", "r"))
        response = requests.get(self.base_url + path, headers=headers, params=params)

        if response.status_code == 401:
            return print("!!! Try to set Cookie")

        return response

    def get_courses(self, _filter=None) -> list[Course]:
        response = self.get(
            "/api/micro-lms/courses/student?limit=10000&state=published"
        )

        if response.status_code == 200:
            courses = [Course(**i) for i in response.json()["items"]]

            return list(filter(_filter, courses))

    def get_course_weeks(self, course_id, _filter=None) -> list[Week]:
        response = self.get(f"/api/micro-lms/courses/{course_id}/overview")

        if response.status_code == 200:
            data = response.json()["themes"]

            weeks = [
                Week(**theme)
                for theme in data
                if "Неделя" in theme["name"] or "Week" in theme["name"]
            ]
            return list(filter(_filter, weeks))
        return []

    def get_course_week(self, course_id, week) -> Week:
        return self.get_course_weeks(course_id)[week - 1]

    def get_course_materials(self, section_id) -> list[File]:
        response = self.get(
            f"/api/micro-lms/longreads/{section_id}/materials?limit=10000"
        )

        if response.status_code == 200:
            data: dict = response.json()

            return [
                File(**file)
                for file in data.get("items", [])
                if file["discriminator"] == "file"
            ]

    def download_course_file(self, filename: str, version: str, filepath: str):
        params = dict(filename=filename, version=version)
        response = self.get("/api/micro-lms/content/download-link", params=params)

        if response.status_code == 200:
            data = response.json()

            if "url" in data:
                download_url = data["url"]
                file = requests.get(download_url)

                if file.status_code == 200 and len(file.content) > 1_000:
                    with open(filepath, "wb") as f:
                        f.write(file.content)
