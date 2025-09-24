import argparse
from pathlib import Path

from cu_lms import LMSClient, Course, Settings


def main():
    p = argparse.ArgumentParser(description="Скачать материалы курса/недели.")
    p.add_argument(
        "--headers",
        default=None,
        help="Путь к headers.json (по умолчанию ./headers.json)",
    )
    p.add_argument(
        "--timeout", default=None, help="Таймауты, формат: connect,read (сек)"
    )
    p.add_argument("--course", help="Точное имя курса")
    p.add_argument("--course-like", help="Подстрока в названии курса")
    p.add_argument("--week", type=int, help="Номер недели (1..N)")
    p.add_argument("--out", default="./downloads", help="Папка для сохранения")
    args = p.parse_args()

    timeout = None
    if args.timeout:
        try:
            c, r = args.timeout.split(",")
            timeout = (int(c), int(r))
        except Exception:
            p.error("Неверный формат --timeout, нужен 'connect,read'")

    settings = Settings(
        base_url=Settings().base_url,
        headers_path=Path(args.headers) if args.headers else Settings().headers_path,
        timeout=timeout or Settings().timeout,
    )
    client = LMSClient(settings)

    def by_exact(c: Course) -> bool:
        return args.course is None or c.name == args.course

    def by_like(c: Course) -> bool:
        return args.course_like is None or (args.course_like.lower() in c.name.lower())

    courses = [c for c in client.get_courses() if by_exact(c) and by_like(c)]
    if not courses:
        print("Курсы не найдены по заданным фильтрам.")
        return 1

    out_dir = Path(args.out)

    for course in courses:
        if args.week:
            weeks = [client.get_course_week(course.id, args.week)]
        else:
            weeks = client.get_course_weeks(course.id)

        for week in weeks:
            saved = client.download_week_files(course, week, out_dir)
            print(f"[{course.name}] {week.name}: сохранено файлов — {len(saved)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
