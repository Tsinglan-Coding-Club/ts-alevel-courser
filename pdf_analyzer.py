from pypdf import PdfReader
import json
import os
from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType  # noqa
from cozepy import COZE_CN_BASE_URL
coze_api_token = "pat_B4bTezzcbob9ri0JHmvCZorL05FYgSStGCE6QxeoBgoO9kgSBfl1h1mHQF2lFl0a"
coze_api_base = COZE_CN_BASE_URL
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)
#BASE_URL = "https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload"
BASE_URL = "https://pdf.v1an.xyz"

import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from pastpaper.models import Subject, Unit, Question

def read_pdf_content(pdf_path):
    reader = PdfReader(f"{pdf_path}")
    content = {}

    for page_index, page in enumerate(reader.pages, start=1):  # pages are 1-based
        text = page.extract_text() or ""
        content[f"Page {page_index}"] = text

    return content

def questions_to_syllabus(qp_pdf_name: str, syllabus_content: str):
    workflow_id = '7579823529422012452'

    reader = PdfReader(f"media/{qp_pdf_name}")
    all_text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        all_text += page.extract_text() or ""
    
    workflow = coze.workflows.runs.create(
        workflow_id=workflow_id,
        parameters={
            "qp_content": all_text,
            "syllabus_content": syllabus_content
        }
    )

    return json.loads(workflow.data)['output']

def pdf_to_questions(qp_pdf_name: str):
    workflow_id = '7580352936451571747'
    workflow = coze.workflows.runs.create(
        workflow_id=workflow_id,
        parameters={
            "qp_content": str(read_pdf_content(f"media/{qp_pdf_name}"))
        }
    )

    return json.loads(workflow.data)['output']

def pdf_to_markscheme(ms_pdf_name: str):
    workflow_id = '7580225688701534260'
    workflow = coze.workflows.runs.create(
        workflow_id=workflow_id,
        parameters={
            "ms_content": str(read_pdf_content(f"media/{ms_pdf_name}"))
        }
    )

    return json.loads(workflow.data)['output']

def pdf_to_syllabus(sy_pdf_name: str):
    workflow_id = '7580533237362688010'
    workflow = coze.workflows.runs.create(
        workflow_id=workflow_id,
        parameters={
            "sy_content": str(read_pdf_content(f"media/{sy_pdf_name}"))
        }
    )

    return json.loads(workflow.data)['output']

if __name__ == "__main__":
    code = "9618"
    year = "s22"
    paper = "13"
    syllabus_content = open(f"coze-workflow/{code}/{code}_syllabus_summary.txt", "r", encoding="utf-8").read()
    qp_pdf_name = f"{code}_{year}_qp_{paper}.pdf"
    ms_pdf_name = qp_pdf_name.replace("qp", "ms")

    qp_data = pdf_to_questions(qp_pdf_name)
    ms_data = pdf_to_markscheme(ms_pdf_name)
    sy_data = questions_to_syllabus(qp_pdf_name, syllabus_content)
    print(qp_data, ms_data, sy_data)
    
    # validate if question number is consistent across all three
    if not (set(qp_data.keys()) == set(ms_data.keys()) == set(sy_data.keys())):
        print("Error: Question numbers are inconsistent across Question Paper, Mark Scheme, and Syllabus analysis.")
        sys.exit(1)
    """sy_pages = pdf_to_questions(f"{code}-2021-2023-syllabus.pdf")

    for unit in sy_pages.keys():
        Unit.objects.update_or_create(
            subject=cs_subject,
            unit_num=int(unit.split()[-1]),
            defaults={'name': unit, 'syllabus_page': sy_pages[unit]},
        )"""

    cs_subject, _ = Subject.objects.get_or_create(
        code='cs'
    )
    
    for i in qp_data.keys():
        print(f"{i}: Question page: {qp_data.get(i, 'N/A')}, Markscheme page: {ms_data.get(i, 'N/A')}, Syllabus page: {sy_data.get(i, 'N/A')}")
        for unit in sy_data[i]:
            unit = Unit.objects.get(subject=cs_subject, unit_num=int(unit.split()[-1]))

            Question.objects.update_or_create(
                code=f"{code}_{year}_{paper}-{i}",
                defaults={
                    'subject': cs_subject,
                    'unit': unit,
                    'qpage': qp_data[i],
                    'apage': ms_data[i],
                }
            )
            defaults={
                    'subject': cs_subject,
                    'unit': unit,
                    'qpage': qp_data[i],
                    'apage': ms_data[i],
                }
            print(f"Created question {i}: {defaults}")
    print("Done.")

    '''
    qp_data = {'Q1': 2, 'Q2': 3, 'Q3': 6, 'Q4': 7, 'Q5': 10, 'Q6': 12}
    ms_data = {'Q1': 3, 'Q2': 3, 'Q3': 5, 'Q4': 5, 'Q5': 7, 'Q6': 8}
    sy_data = {'Q1': ['Unit 1'], 'Q2': ['Unit 3'], 'Q3': ['Unit 6'], 'Q4': ['Unit 8'], 'Q5': ['Unit 5'], 'Q6': ['Unit 4']}
    sy_pages = json.loads("""{
    "Unit 1": 13,
    "Unit 10": 26,
    "Unit 11": 27,
    "Unit 12": 28,
    "Unit 13": 29,
    "Unit 14": 30,
    "Unit 15": 31,
    "Unit 16": 31,
    "Unit 17": 32,
    "Unit 18": 33,
    "Unit 19": 33,
    "Unit 2": 15,
    "Unit 20": 34,
    "Unit 3": 16,
    "Unit 4": 18,
    "Unit 5": 21,
    "Unit 6": 22,
    "Unit 7": 23,
    "Unit 8": 23,
    "Unit 9": 25}""")
    print(qp_data, ms_data, sy_data, sy_pages)'''