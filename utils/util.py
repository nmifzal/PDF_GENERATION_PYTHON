import math
import json
import os
import plotly.express as px
import pandas as pd

dmk_red_color = "#ab2d24"

PARTY_WISE_COLORS = {
    "DMK": "#ab2d24",
    "VCK": "#f7e048",
    "AIADMK": "#215e1b",
    "Others": "#0460e0",
    "PMK": "#f57ddf",
}


def model_data(response_data=[], payload={}):
    SUMMARY_ITEMS_PER_PAGE = 10
    INDEX_ITEMS_PER_PAGE = 10
    APPENDIX_ITEMS_PER_PAGE = 10

    with open(
        os.path.abspath("utils/ac_number_to_name.json"), "r", encoding="utf-8"
    ) as f:
        ac_number_to_name = json.load(f)

    AC_NO = payload.get("ac_no", None)
    AC_NAME = ac_number_to_name["ta"][str(AC_NO)]
    YEARS_LIST = payload.get("year", [])
    GRAPH_FORMAT = len(YEARS_LIST)

    summary_data_pages = []
    index_data_pages = []
    appendix_data_pages = []

    # GET SUMMARY PAGE DATA
    summary_main_data = response_data["summary_data"]
    summary_data_count = len(summary_main_data)

    if summary_data_count < SUMMARY_ITEMS_PER_PAGE:
        summary_data_pages.append(summary_main_data)
    else:
        number_of_iterations = math.ceil(summary_data_count / SUMMARY_ITEMS_PER_PAGE)

        for x in range(number_of_iterations):
            slice_from = 0
            slice_till = 0 + SUMMARY_ITEMS_PER_PAGE

            summary_data_pages.append(summary_main_data[slice_from:slice_till])

            slice_from = slice_from + SUMMARY_ITEMS_PER_PAGE
            slice_till = slice_till + SUMMARY_ITEMS_PER_PAGE
    #
    #
    #

    # GET INDEX PAGE DATA
    index_main_data = response_data["index_data"]
    index_data_count = len(index_main_data)

    if index_data_count < INDEX_ITEMS_PER_PAGE:
        index_data_pages.append(index_main_data)
    else:
        number_of_iterations = math.ceil(index_data_count / INDEX_ITEMS_PER_PAGE)

        for x in range(number_of_iterations):
            slice_from = 0
            slice_till = 0 + INDEX_ITEMS_PER_PAGE

            index_data_pages.append(index_main_data[slice_from:slice_till])

            slice_from = slice_from + INDEX_ITEMS_PER_PAGE
            slice_till = slice_till + INDEX_ITEMS_PER_PAGE
    #
    #
    #

    # GET APPENDIX PAGE DATA
    appendix_main_data = response_data["appendix"]
    appendix_data_count = len(appendix_main_data)

    if appendix_data_count < APPENDIX_ITEMS_PER_PAGE:
        appendix_data_pages.append(appendix_main_data)
    else:
        number_of_iterations = math.ceil(appendix_data_count / APPENDIX_ITEMS_PER_PAGE)

        for x in range(number_of_iterations):
            slice_from = 0
            slice_till = 0 + APPENDIX_ITEMS_PER_PAGE

            appendix_data_pages.append(appendix_main_data[slice_from:slice_till])

            slice_from = slice_from + APPENDIX_ITEMS_PER_PAGE
            slice_till = slice_till + APPENDIX_ITEMS_PER_PAGE
    #
    #
    #

    #
    #
    #
    graph_main_data = response_data["graph_data"]

    new_graph_data = {}

    for item_key in graph_main_data:
        new_graph_data[item_key] = []

        booth_pair = []

        for idx, (key, value) in enumerate(graph_main_data[item_key].items()):
            YEAR_WISE_DATA = []

            for year in YEARS_LIST:
                year_value = value.get(year)

                new_year_data = {
                    **year_value,
                    "fig": convert_graph_data_into_fig(
                        graph_data=year_value["graph_data"]
                    ),
                    "year": year,
                }

                YEAR_WISE_DATA.append(new_year_data)

            booth_pair.append(
                {
                    **value,
                    "booth_no": key,
                    "year_wise_data": YEAR_WISE_DATA,
                }
            )

            if idx % 2 == 0:
                pass
            else:
                new_graph_data[item_key].append(booth_pair)
                booth_pair = []
    #
    #
    #

    return {
        "AC_NAME": AC_NAME,
        "summary_data_pages": summary_data_pages,
        "index_data_pages": index_data_pages,
        "appendix_data_pages": appendix_data_pages,
        "COMPARE_TYPE": payload.get("compare_type"),
        "graph_data": new_graph_data,
        "YEARS_LIST": YEARS_LIST,
        "GRAPH_FORMAT": GRAPH_FORMAT,
    }


def convert_graph_data_into_fig(graph_data):
    graph_color = "#e3e2e1"

    x_axis = graph_data["x"]
    y_axis = graph_data["y"]

    df = pd.DataFrame({"parties": x_axis, "votes": y_axis})
    figure = px.bar(df, x="parties", y="votes")

    figure.update_layout(
        {
            "paper_bgcolor": graph_color,
            "plot_bgcolor": graph_color,
            "font": {
                "size": 7,
                "family": "'Inter', 'sans serif'",
            },
            "showlegend": False,
            "height": 150,
            "width": 200,
            "margin": {
                "b": 0,
                "l": 0,
                "r": 0,
                "t": 0,
            },
        },
    )

    if x_axis == None:
        marker_color = [dmk_red_color]
    else:
        marker_color = [PARTY_WISE_COLORS.get(party, dmk_red_color) for party in x_axis]

    figure.update_traces(marker_color=marker_color, textposition="outside")

    return figure.to_html(full_html=False)
