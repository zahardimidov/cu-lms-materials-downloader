from typing import List
from pydantic import BaseModel, Field


class Parent(BaseModel):
    name: str

    @property
    def path(self) -> str:
        return self.name

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class Course(Parent):
    id: int
    state: str
    isArchived: bool


class Section(Parent):
    id: int
    type: str


class Week(Parent):
    id: int
    sections: List[Section] = Field(default_factory=list, alias="longreads")


class FileModel(BaseModel):
    discriminator: str
    viewType: str | None = None
    mediaType: str | None = None
    filename: str
    version: str
    length: int
