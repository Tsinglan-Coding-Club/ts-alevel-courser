#!/usr/bin/env python
"""
Scan media files and auto create PastPaper records.
Repeated runs are safe because existing codes are skipped.
"""
import os
import re
from collections import defaultdict

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from pastpaper.models import PastPaper, Subject  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
FILENAME_PATTERN = re.compile(
    r"(?P<exam>\d{3,4})_(?P<session>[sw])(?P<year>\d{2})_(?P<kind>ms|qp)_(?P<paper>\d{2,2})\.pdf$",
    re.IGNORECASE,
)


def discover_pastpapers(media_root: str):
    """
    Yield tuples (exam_code, session, year_suffix, paper_num) parsed from filenames.
    Only unique combinations (ignoring qp/ms duplication) are returned.
    """
    discovered = set()
    for entry in os.listdir(media_root):
        path = os.path.join(media_root, entry)
        if not os.path.isfile(path):
            continue
        match = FILENAME_PATTERN.match(entry)
        if not match:
            continue
        exam_code = match.group("exam")
        session = match.group("session").lower()
        year_suffix = match.group("year")
        paper_num = match.group("paper")
        key = (exam_code, session, year_suffix, paper_num)
        if key not in discovered:
            discovered.add(key)
            yield key


def main():
    if not os.path.isdir(MEDIA_ROOT):
        raise SystemExit(f"Media directory not found: {MEDIA_ROOT}")

    grouped = defaultdict(list)
    for exam_code, session, year_suffix, paper_num in discover_pastpapers(MEDIA_ROOT):
        grouped[exam_code].append((session, year_suffix, paper_num))

    if not grouped:
        print("No matching media files found. Nothing to insert.")
        return

    total_created = 0
    for exam_code, papers in grouped.items():
        try:
            subject = Subject.objects.get(exam_code=exam_code)
        except Subject.DoesNotExist:
            print(f"Subject with exam_code={exam_code} not found. Skipping related files.")
            continue

        for session, year_suffix, paper_num in papers:
            code = f"{exam_code}_{session}{year_suffix}_{paper_num}"
            year = 2000 + int(year_suffix)
            _, created = PastPaper.objects.get_or_create(
                code=code,
                defaults={
                    "subject": subject,
                    "year": year,
                    "session": session,
                    "paper_num": paper_num,
                },
            )
            total_created += int(created)
            action = "Created" if created else "Exists"
            print(f"{action}: {code}")

    print(f"\nFinished. PastPaper records created this run: {total_created}")


if __name__ == "__main__":
    main()
