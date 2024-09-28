# utils/report_generator.py
import pandas as pd
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def clean_text(text):
    text = re.sub(r'[\[\]\'\"]', '', text)
    text = text.replace('\\n', '\n')
    return text

def parse_markdown(text, styles):
    elements = []
    paragraphs = text.split('\n\n')

    for paragraph in paragraphs:
        lines = paragraph.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('###'):
                elements.append(Paragraph(line.strip('#').strip(), styles['Heading3']))
            elif line.startswith('##'):
                elements.append(Paragraph(line.strip('#').strip(), styles['Heading2']))
            elif line.startswith('#'):
                elements.append(Paragraph(line.strip('#').strip(), styles['Heading1']))
            elif '**' in line:
                parts = re.split(r'(\*\*.*?\*\*)', line)
                formatted_parts = []
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        formatted_parts.append(f'<b>{part[2:-2]}</b>')
                    else:
                        formatted_parts.append(part)
                elements.append(Paragraph(''.join(formatted_parts), styles['BodyText']))
            else:
                elements.append(Paragraph(line, styles['BodyText']))

        elements.append(Spacer(1, 12))

    return elements

def markdown_to_pdf(df, output_filename, project_name):
    doc = SimpleDocTemplate(output_filename, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles['Heading1'].fontSize = 18
    styles['Heading2'].fontSize = 16
    styles['Heading3'].fontSize = 14

    elements = [Paragraph(project_name, styles['Title']), Spacer(1, 24)]

    for index, row in df.iterrows():
        for column, value in row.items():
            if column != 'index':
                cleaned_text = clean_text(str(value))
                elements.extend(parse_markdown(cleaned_text, styles))

        elements.append(Spacer(1, 24))

    doc.build(elements)
    print('PDF created successfully')
