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
import time
import timeit
from weasyprint import HTML


def generate_pdf():
    OUTPUT_FILE_PATH = "templates/output.html"
    OUTPUT_PDF_PATH = "pdf_output/sample3.pdf"

    with open(os.path.abspath(OUTPUT_FILE_PATH), "w") as f:
        f.write("")

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
        "year": [
            "2016",
            "2024",
        ],
        # "year": [
        #     "2016",
        #     "2019",
        #     "2021",
        #     "2024",
        # ],
        "local_body": ["காணை தெற்கு", "காணை வடக்கு"],
        "compare_type": "booth",
    }

    COLORS = [
        "ca_graph_component_pink_bg",
        "ca_graph_component_blue_bg",
        "ca_graph_component_green_bg",
        "ca_graph_component_indigo_bg",
    ]

    template = env.get_template(
        "main_template.html",
    )

    # with open("response_2_year_original.json", "r", encoding="utf-8") as f:
    with open("response_2_year_truncated.json", "r", encoding="utf-8") as f:
        # with open("response_4_year_original.json", "r", encoding="utf-8") as f:
        # with open("response_4_year_truncated.json", "r", encoding="utf-8") as f:
        response_data = json.load(f)
        modelled_data = model_data(response_data=response_data, payload=payload)

    html = template.render(
        DATA=modelled_data,
        COLORS=COLORS,
    )

    # to save the results
    with open("templates/output.html", "w", encoding="utf-8") as f:
        f.write(html)

    # # # using pdfkit
    # config = pdfkit.configuration(
    #     wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
    # )
    # pdfkit.from_file(
    #     "templates/output.html",
    #     "pdf_output/sample3.pdf",
    #     configuration=config,
    #     options={
    #             "enable-local-file-access": "",
    #             "encoding": "UTF-8",
    #             },
    # )

    print("HTML GENERATED")

    # # using pyhtml2pdf
    converter.convert(
        f"file:///{os.path.abspath(OUTPUT_FILE_PATH)}",
        OUTPUT_PDF_PATH,
        print_options={"preferCSSPageSize": True, "printBackground": True},
    )

    # Load the HTML file
    # html = HTML(filename=OUTPUT_FILE_PATH)
    # html.write_pdf(OUTPUT_PDF_PATH)

    # time.sleep(3)
    # delete the output html file as it is not necessary after pdf is created
    if os.path.exists(OUTPUT_FILE_PATH):
        os.remove(OUTPUT_FILE_PATH)
    else:
        print("The file does not exist")


execution_time = timeit.timeit(stmt=generate_pdf, number=1)
print(f"Execution time: {execution_time} seconds")
