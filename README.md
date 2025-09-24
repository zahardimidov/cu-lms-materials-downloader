# cu_lms

Удобный клиент для работы с API Central University.

## Быстрый старт

1) Скопируйте `headers.example.json` → `headers.json` заполните значения (как минимум Cookie).
2) Пример: скачать все файлы из недели курса:
```bash
python main.py --course "Название курса" --week 1 --out ./downloads
```
или отфильтровать курсы:
```bash
python main.py --course-like "Python" --week 2
```