import logging
import json
import os
import concurrent.futures
import multiprocessing
from pyhtml2pdf import converter
from jinja2 import Environment, select_autoescape, FileSystemLoader
from utils.util import model_data
import timeit
from PyPDF2 import PdfMerger

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_available_processors():
    return multiprocessing.cpu_count()


def generate_component_pdf(component_name, template_file, output_file, response_json, payload):
    OUTPUT_HTML_PATH = f"templates/output_{component_name}.html"
    OUTPUT_PDF_PATH = f"pdf_output/{output_file}"

    env = Environment(
        loader=FileSystemLoader("templates", encoding="utf-8"),
        autoescape=select_autoescape,
    )

    COLORS = [
        "ca_graph_component_pink_bg",
        "ca_graph_component_blue_bg",
        "ca_graph_component_green_bg",
        "ca_graph_component_indigo_bg",
    ]

    template = env.get_template(template_file)

    with open(response_json, "r", encoding="utf-8") as f:
        response_data = json.load(f)
        modelled_data = model_data(
            response_data=response_data, payload=payload)

    render_data = {
        "summary_data_pages": modelled_data.get("summary_data_pages", []),
        "index_data_pages": modelled_data.get("index_data_pages", []),
        "graph_data": modelled_data.get("graph_data", {}),
        "appendix_data_pages": modelled_data.get("appendix_data_pages", []),
        "AC_NAME": modelled_data.get("AC_NAME", ""),
        "YEARS_LIST": modelled_data.get("YEARS_LIST", []),
        "HEADER": modelled_data.get("HEADER", ""),
        "COLORS": COLORS,
        "GRAPH_DATA": modelled_data.get("graph_data", {}),
        "GRAPH_FORMAT": modelled_data.get("GRAPH_FORMAT", 2)
    }

    html = template.render(**render_data)

    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        converter.convert(
            f"file:///{os.path.abspath(OUTPUT_HTML_PATH)}",
            OUTPUT_PDF_PATH,
            print_options={"preferCSSPageSize": True, "printBackground": True},
        )

        if os.path.exists(OUTPUT_HTML_PATH):
            os.remove(OUTPUT_HTML_PATH)

        return OUTPUT_PDF_PATH

    except Exception as e:
        logging.error(f"Error generating PDF for {component_name}: {str(e)}")
        return None


def combine_pdfs(pdf_paths, output_path):
    merger = PdfMerger()
    for pdf in pdf_paths:
        if pdf and os.path.exists(pdf):
            merger.append(pdf)
    merger.write(output_path)
    merger.close()
    logging.info(f"Combined PDF created at: {output_path}")


def generate_all_pdfs():
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

    response_json = "response_2_year_truncated.json"

    components = [
        ("graph", "graph_page.html", "graph.pdf"),
        ("summary", "summary_page.html", "summary.pdf"),
        ("index", "index_page.html", "index.pdf"),
        ("appendix", "appendix_page.html", "appendix.pdf")
    ]

    available_processors = get_available_processors()
    threads = min(available_processors, len(components))

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_component = {executor.submit(generate_component_pdf, component_name, template_file, output_file, response_json, payload): component_name
                               for component_name, template_file, output_file in components}

        pdf_paths = []
        for future in concurrent.futures.as_completed(future_to_component):
            component_name = future_to_component[future]
            try:
                pdf_path = future.result()
                if pdf_path:
                    pdf_paths.append(pdf_path)
                    logging.info(
                        f"PDF for {component_name} generated successfully")
            except Exception as e:
                logging.error(
                    f"Error generating PDF for {component_name}: {str(e)}")

    combined_pdf_path = "pdf_output/combined_report.pdf"
    combine_pdfs(pdf_paths, combined_pdf_path)

    for pdf_path in pdf_paths:
        os.remove(pdf_path)


if __name__ == "__main__":
    logging.info("Starting PDF generation process")
    execution_time = timeit.timeit(stmt=generate_all_pdfs, number=1)
    logging.info(f"Execution time: {execution_time} seconds")
    logging.info("PDF generation process completed")
