#!/usr/bin/env python
"""
填充示例数据脚本 - 支持多学科
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from pastpaper.models import Subject, Unit, Question, PastPaper

# 创建学科
print("Creating subjects...")
cs_subject, _ = Subject.objects.get_or_create(
    code='cs',
    defaults={
        'name': 'CIE A-Level Computer Science',
        'exam_code': '9618',
        'syllabus_url': 'https://cdn.computerscience.vip/pdf/9618-2021-2023-syllabus.pdf'
    }
)

ig_subject, _ = Subject.objects.get_or_create(
    code='ig',
    defaults={
        'name': 'CIE IGCSE Computer Science',
        'exam_code': '0984',
        'syllabus_url': ''
    }
)

print(f"Created subjects: {cs_subject}, {ig_subject}")

# 创建A-Level CS的20个单元
print("Creating units for A-Level CS...")
unit_names = [
    "Information representation",
    "Communication and Internet technologies",
    "Hardware",
    "Processor fundamentals",
    "System software",
    "Security, privacy and data integrity",
    "Ethics and ownership",
    "Databases",
    "Algorithm design and problem-solving",
    "Data types and structures",
    "Programming",
    "Software development",
    "Data representation",
    "Communication",
    "Hardware and virtual machines",
    "System software",
    "Security",
    "Artificial intelligence (AI)",
    "Computational thinking and problem-solving",
    "Further programming"
]

for i, name in enumerate(unit_names, 1):
    Unit.objects.get_or_create(
        subject=cs_subject,
        unit_num=i,
        defaults={'name': name}
    )

print(f"Created {len(unit_names)} units for A-Level CS")

# 创建A-Level CS的示例题目（Unit 1）
print("Creating sample questions for Unit 1...")
unit1 = Unit.objects.get(subject=cs_subject, unit_num=1)

questions_data = [
    {"code": "9618_w22_11-Q1", "qpage": 2, "apage": 1},
    {"code": "9618_s22_11-Q1", "qpage": 2, "apage": 1},
    {"code": "9618_s23_13-Q7a", "qpage": 15, "apage": 10},
    {"code": "9618_w23_13-Q2", "qpage": 4, "apage": 2},
    {"code": "9618_w23_13-Q1", "qpage": 2, "apage": 1},
    {"code": "9618_w23_12-Q6", "qpage": 12, "apage": 7},
    {"code": "9618_w23_12-Q3", "qpage": 5, "apage": 3},
    {"code": "9618_w23_11-Q1", "qpage": 2, "apage": 1},
    {"code": "9618_s23_12-Q4", "qpage": 8, "apage": 5},
    {"code": "9618_s23_11-Q1", "qpage": 2, "apage": 1},
]

for q_data in questions_data:
    Question.objects.get_or_create(
        code=q_data["code"],
        defaults={
            'subject': cs_subject,
            'unit': unit1,
            'qpage': q_data["qpage"],
            'apage': q_data["apage"],
            'spage': 1
        }
    )

print(f"Created {len(questions_data)} questions for Unit 1")

# 创建Past Papers数据
print("Creating past papers...")
past_papers_data = [
    # 2023
    {"code": "9618_s23_11", "year": 2023, "session": "s", "paper_num": "11"},
    {"code": "9618_s23_12", "year": 2023, "session": "s", "paper_num": "12"},
    {"code": "9618_s23_13", "year": 2023, "session": "s", "paper_num": "13"},
    {"code": "9618_w23_11", "year": 2023, "session": "w", "paper_num": "11"},
    {"code": "9618_w23_12", "year": 2023, "session": "w", "paper_num": "12"},
    {"code": "9618_w23_13", "year": 2023, "session": "w", "paper_num": "13"},
    # 2022
    {"code": "9618_s22_11", "year": 2022, "session": "s", "paper_num": "11"},
    {"code": "9618_s22_12", "year": 2022, "session": "s", "paper_num": "12"},
    {"code": "9618_w22_11", "year": 2022, "session": "w", "paper_num": "11"},
    {"code": "9618_w22_12", "year": 2022, "session": "w", "paper_num": "12"},
]

for pp_data in past_papers_data:
    PastPaper.objects.get_or_create(
        code=pp_data["code"],
        defaults={
            'subject': cs_subject,
            'year': pp_data["year"],
            'session': pp_data["session"],
            'paper_num': pp_data["paper_num"]
        }
    )

print(f"Created {len(past_papers_data)} past papers")

print("\n✅ Data population completed!")
print(f"Subjects: {Subject.objects.count()}")
print(f"Units: {Unit.objects.count()}")
print(f"Questions: {Question.objects.count()}")
print(f"Past Papers: {PastPaper.objects.count()}")

