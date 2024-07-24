import logging
import json
import os
from pyhtml2pdf import converter
from jinja2 import (
    Environment,
    select_autoescape,
    Template,
    FileSystemLoader,
)
import pdfkit
import math
from utils.util import model_data

# path = os.path.abspath("assets/main_template.html")
path = os.path.abspath("templates/output.html")

env = Environment(
    loader=FileSystemLoader("templates", encoding="utf-8"),
    autoescape=select_autoescape,
)

payload = {
    "trend": True,
    "party": ["DMK", "AIADMK", "PMK", "CPI", "CPI(M)", "VCK", "MDMK"],
    "ac_no": 75,
    "pc_no": 13,
    "year": ["2019", "2024"],
    "local_body": ["காணை தெற்கு", "காணை வடக்கு"],
    "compare_type": "booth",
}

COLORS = [
    "ca_graph_component_blue_bg",
    "ca_graph_component_pink_bg",
    "ca_graph_component_indigo_bg",
    "ca_graph_component_green_bg",
]

template = env.get_template(
    "main_template.html",
)

with open("response.json", "r", encoding="utf-8") as f:
    response_data = json.load(f)
    modelled_data = model_data(response_data=response_data, payload=payload)


html = template.render(
    DATA=modelled_data,
    COLORS=COLORS,
)

# to save the results
with open("templates/output.html", "w", encoding="utf-8") as f:
    f.write(html)

# # using pdfkit
config = pdfkit.configuration(
    wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
)
# pdfkit.from_file(
#     "templates/output.html",
#     "pdf_output/sample3.pdf",
#     configuration=config,
#     options={"enable-local-file-access": ""},
# )

# using pyhtml2pdf
converter.convert(
    f"file:///{path}",
    "pdf_output/sample3.pdf",
    print_options={"preferCSSPageSize": True, "printBackground": True},
)
