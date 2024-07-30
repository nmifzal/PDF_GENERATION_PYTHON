import json
import os
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError, TemplateNotFound
from pyhtml2pdf import converter
from PyPDF2 import PdfMerger

from utils.util import model_data

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

components = [
    # ("Main", "main_template.html", "main_template.pdf"),
    ("summary", "summary_page.html", "summary.pdf"),
    ("index", "index_page.html", "index.pdf"),
    ("graph", "graph_page.html", "graph.pdf"),
    ("appendix", "appendix_page.html", "appendix.pdf")
]


def render_template(template_path, context):
    try:
        env = Environment(loader=FileSystemLoader(
            os.path.dirname(template_path)))
        template = env.get_template(os.path.basename(template_path))
        return template.render(context)
    except TemplateNotFound as e:
        logging.error(f"Template not found: {e}")
        raise
    except TemplateSyntaxError as e:
        logging.error(f"Template syntax error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error rendering template: {e}")
        raise


def html_to_pdf(html_path, output_path):
    try:
        converter.convert(
            f"file:///{html_path}",
            output_path,
            print_options={"preferCSSPageSize": True, "printBackground": True}
        )
    except Exception as e:
        logging.error(f"Error converting HTML to PDF: {e}")
        raise


def process_template(name, template_file, output_pdf, context, template_dir):
    start_time = time.time()

    template_path = os.path.join(template_dir, template_file)
    output_pdf_path = os.path.join(output_dir, output_pdf)

    try:
        html_content = render_template(template_path, context)

        # Save HTML content to a file inside the templates directory
        html_file_path = os.path.join(template_dir, f"{name}_temp.html")
        with open(html_file_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)

        html_to_pdf(html_file_path, output_pdf_path)

        # Optionally remove the HTML file
        os.remove(html_file_path)

        duration = time.time() - start_time
        logging.info(
            f"Converted {template_file} to {output_pdf} in {duration:.2f} seconds")
    except Exception as e:
        logging.error(f"Failed to process {template_file}: {e}")


def main(template_dir, output_dir, context):
    start_time = time.time()

    if not os.path.exists(template_dir):
        raise FileNotFoundError(
            f"Template directory not found: {template_dir}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf_files = []

    with ThreadPoolExecutor() as executor:
        futures = []
        for component in components:
            name, template_file, output_pdf = component
            pdf_path = os.path.join(output_dir, output_pdf)
            pdf_files.append(pdf_path)
            futures.append(executor.submit(process_template, name,
                           template_file, output_pdf, context, template_dir))

        for future in as_completed(futures):
            future.result()  # This will raise an exception if the task failed

    # Merge PDFs
    try:
        merger = PdfMerger()
        for pdf in pdf_files:
            merger.append(pdf)

        merged_pdf = os.path.join(output_dir, "merged_output.pdf")
        merger.write(merged_pdf)
        merger.close()

        # Log PDF merging duration
        merge_duration = time.time() - start_time
        logging.info(
            f"All PDFs merged into {merged_pdf} in {merge_duration:.2f} seconds")
    except Exception as e:
        logging.error(f"Failed to merge PDFs: {e}")

    # Optionally, remove individual PDF files
    for pdf in pdf_files:
        try:
            os.remove(pdf)
        except Exception as e:
            logging.error(f"Failed to remove PDF file {pdf}: {e}")


if __name__ == "__main__":
    # Use absolute paths or paths relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, "templates")
    output_dir = os.path.join(script_dir, "output")

    payload = {
        "trend": True,
        "party": ["DMK", "AIADMK", "PMK", "CPI", "CPI(M)", "VCK", "MDMK"],
        "ac_no": 75,
        "pc_no": 13,
        "year": [
            "2016",
            "2024",
        ],
        "local_body": ["காணை தெற்கு", "காணை வடக்கு"],
        "compare_type": "booth",
    }

    # response_json = "response_2_year_original.json"
    # response_json = "response_2_year_truncated.json"
    response_json = "response_4_year_original.json"
    # response_json = "response_4_year_truncated.json"

    COLORS = [
        "ca_graph_component_pink_bg",
        "ca_graph_component_blue_bg",
        "ca_graph_component_green_bg",
        "ca_graph_component_indigo_bg",
    ]

    with open(response_json, "r", encoding="utf-8") as f:
        response_data = json.load(f)
        modelled_data = model_data(
            response_data=response_data, payload=payload)

    render_data = {
        "summary_data_pages": modelled_data.get("summary_data_pages", []),
        "index_data_pages": modelled_data.get("index_data_pages", []),
        "appendix_data_pages": modelled_data.get("appendix_data_pages", []),
        "AC_NAME": modelled_data.get("AC_NAME", ""),
        "YEARS_LIST": modelled_data.get("YEARS_LIST", []),
        "HEADER": modelled_data.get("HEADER", ""),
        "COLORS": COLORS,
        "GRAPH_DATA": modelled_data.get("graph_data", {}),
        "GRAPH_FORMAT": modelled_data.get("GRAPH_FORMAT", 2)
    }

    try:
        main(template_dir, output_dir, render_data)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
