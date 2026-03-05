import os
import unicodedata

from lms import LMS

lms = LMS()

cnt = 0

BLACKLIST = [
    "Безопасность жизнедеятельности",
    "Ознакомление с локально-нормативными актами",
    "Пульс-опрос. Бакалавриат",
    "Физкультура",
    "Основы разработки на Go",
]


def create_filename(filename: str, course_name: str, week_name: str):
    parts = []

    filename = unicodedata.normalize("NFC", filename)
    course_name = unicodedata.normalize("NFC", course_name)
    week_name = unicodedata.normalize("NFC", week_name)

    ext = filename.split(".")[-1]

    for part in filename.replace(ext, "").split("_"):
        p = (
            part.replace(course_name, "")
            .replace(week_name, "")
            .replace("№", "")
            .strip(" .:-_")
        )

        if p:
            parts.append(p)

    if not any(["Неделя" in i for i in parts]):
        parts.insert(0, week_name)
    return "__".join(parts) + f".{ext}"


for course in lms.get_courses(
    _filter=lambda x: all(i not in x.name for i in BLACKLIST)
):
    print("\n", course.name)
    weeks = lms.get_course_weeks(course.id, lambda week: "5" in week.name) # FILTER !!!

    path = "/Users/zahardimidov/Documents/Учеба/Семестр второй/" + course.path

    for week in weeks:
        print(week.name)
        os.makedirs(path + "/" + week.path + "/ДЗ", exist_ok=True)

        for section in week.sections:
            materials = lms.get_course_materials(section.id)

            if not materials:
                continue

            print(section.name)

            for file in materials:
                filename = create_filename(
                    filename=file.filename.split("/")[-1],
                    course_name=course.path,
                    week_name=week.path,
                )
                filepath = path + "/" + week.path + "/" + filename

                exists = os.path.exists(filepath)

                print(file.filename, "" if exists else "[new]")
                print(filepath, '\n')

                if exists:
                    continue

                lms.download_course_file(
                    file.filename, version=file.version, filepath=filepath
                )

                cnt += 1
        print()

print(f"Downloaded files: {cnt}")
