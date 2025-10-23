import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from pastpaper.models import Unit, Question

# Create units
units_data = [
    (1, "Information representation"),
    (2, "Communication and Internet technologies"),
    (3, "Hardware"),
    (4, "Logic circuits and Boolean algebra"),
    (5, "Processor fundamentals"),
    (6, "Assembly language programming"),
    (7, "System software"),
    (8, "Security"),
    (9, "Ethics and ownership"),
    (10, "Database and data modelling"),
    (11, "Algorithm design and problem-solving"),
    (12, "Data types and structures"),
    (13, "Programming"),
    (14, "Software development"),
    (15, "Data representation"),
    (16, "Communication"),
    (17, "Hardware"),
    (18, "Processor fundamentals"),
    (19, "System software"),
    (20, "Security, privacy and data integrity"),
]

for unit_num, name in units_data:
    Unit.objects.get_or_create(
        unit_num=unit_num,
        defaults={'name': name, 'subject': 'cs'}
    )

print(f"Created {len(units_data)} units")

# Create sample questions for Unit 1
unit1 = Unit.objects.get(unit_num=1)
questions_data = [
    ("9618_s23_11-Q1", 1, 1, 1),
    ("9618_s23_12-Q4", 1, 4, 1),
    ("9618_w23_11-Q1", 1, 1, 1),
    ("9618_w23_12-Q3", 1, 3, 1),
    ("9618_w23_12-Q6", 1, 6, 1),
    ("9618_w23_13-Q1", 1, 1, 1),
    ("9618_w23_13-Q2", 1, 2, 1),
    ("9618_s23_13-Q7a", 1, 7, 1),
    ("9618_s22_11-Q1", 1, 1, 1),
    ("9618_w22_11-Q1", 1, 1, 1),
]

for code, qpage, apage, spage in questions_data:
    Question.objects.get_or_create(
        code=code,
        defaults={
            'unit': unit1,
            'qpage': qpage,
            'apage': apage,
            'spage': spage
        }
    )

print(f"Created {len(questions_data)} sample questions for Unit 1")
print("Data population completed!")
