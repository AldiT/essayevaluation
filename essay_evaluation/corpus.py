import csv
import re

grade_expression = re.compile('[0-9]+(\.[0-9]+)?')


def read_flip_texts(filepath,
                    column_essay='Essay',
                    column_grade='Vocab_Grade_AVG',
                    column_level='Level',
                    levels=None):
    if levels is None:
        levels = ['A1.1', 'A1.2', 'B1.1', 'B1.2', 'B2.1', 'B2.2', 'C1.1']
        
    texts = []
    grades = []
    text_levels = []
    with open(filepath) as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            text = row[column_essay].replace('\n', ' ')
            score = row[column_grade].strip()
            level = row[column_level].strip()
            if text and grade_expression.match(score) and level in levels:
                texts.append(text)
                grades.append(float(score))
                text_levels.append(level)
    return texts, grades, text_levels


def read_csv(filepath,
                    column_text='Essay',
                    column_grade='Level'):
    texts = []
    grades = []
    with open(filepath) as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            text = row[column_text].replace('\n', ' ')
            grade = row[column_grade].strip()
            if text and grade_expression.match(grade):
                texts.append(text)
                grades.append(float(grade))
    return texts, grades