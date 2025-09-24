import os

from lms import LMS

lms = LMS()


for course in lms.get_courses(
    _filter=lambda x: all(i not in x.name for i in [
        "Нулевой семестр",
        "Физкультура",
        "Ознакомление с локально-нормативными актами",
        "Большие идеи"
    ])
):
    print("\n", course.name)
    weeks = lms.get_course_weeks(course.id)

    path = "/Users/zahardimidov/Documents/Учеба/Семестр первый/" + course.path

    for week in weeks:
        print(week.name)
        os.makedirs(path + "/" + week.path + "/ДЗ", exist_ok=True)

        for section in week.sections:
            materials = lms.get_course_materials(section.id)

            if not materials:
                continue

            print(section.name)

            for file in materials:
                print(file.filename)

                filename = (
                    file.filename.split("/")[-1].replace(course.path, "").strip(" ._")
                )

                filepath = path + "/" + week.path + "/" + filename

                if os.path.exists(filepath):
                    continue

                lms.download_course_file(
                    file.filename, version=file.version, filepath=filepath
                )
        print()
