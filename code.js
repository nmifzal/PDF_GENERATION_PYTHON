const fs = require("fs");
const path = require("path");

function convertGraphDataIntoFig(graphData) {
  // This is a placeholder function. Replace with actual implementation.
  return graphData;
}

function modelData(responseData = {}, payload = {}) {
  const SUMMARY_ITEMS_PER_PAGE = 10;
  const INDEX_ITEMS_PER_PAGE = 10;
  const APPENDIX_ITEMS_PER_PAGE = 10;

  const acNumberToName = JSON.parse(fs.readFileSync(path.resolve("utils/ac_number_to_name.json"), "utf8"));

  const AC_NO = payload.ac_no || null;
  const AC_NAME = acNumberToName["ta"][String(AC_NO)];
  const YEARS_LIST = payload.year || [];
  const GRAPH_FORMAT = YEARS_LIST.length;

  let summaryDataPages = [];
  let indexDataPages = [];
  let appendixDataPages = [];

  // GET SUMMARY PAGE DATA
  const summaryMainData = responseData.summary_data || [];
  const summaryDataCount = summaryMainData.length;

  if (summaryDataCount < SUMMARY_ITEMS_PER_PAGE) {
    summaryDataPages.push(summaryMainData);
  } else {
    const numberOfIterations = Math.ceil(summaryDataCount / SUMMARY_ITEMS_PER_PAGE);
    for (let x = 0; x < numberOfIterations; x++) {
      let sliceFrom = x * SUMMARY_ITEMS_PER_PAGE;
      let sliceTill = sliceFrom + SUMMARY_ITEMS_PER_PAGE;
      summaryDataPages.push(summaryMainData.slice(sliceFrom, sliceTill));
    }
  }

  // GET INDEX PAGE DATA
  const indexMainData = responseData.index_data || [];
  const indexDataCount = indexMainData.length;

  if (indexDataCount < INDEX_ITEMS_PER_PAGE) {
    indexDataPages.push(indexMainData);
  } else {
    const numberOfIterations = Math.ceil(indexDataCount / INDEX_ITEMS_PER_PAGE);
    for (let x = 0; x < numberOfIterations; x++) {
      let sliceFrom = x * INDEX_ITEMS_PER_PAGE;
      let sliceTill = sliceFrom + INDEX_ITEMS_PER_PAGE;
      indexDataPages.push(indexMainData.slice(sliceFrom, sliceTill));
    }
  }

  // GET APPENDIX PAGE DATA
  const appendixMainData = responseData.appendix || [];
  const appendixDataCount = appendixMainData.length;

  if (appendixDataCount < APPENDIX_ITEMS_PER_PAGE) {
    appendixDataPages.push(appendixMainData);
  } else {
    const numberOfIterations = Math.ceil(appendixDataCount / APPENDIX_ITEMS_PER_PAGE);
    for (let x = 0; x < numberOfIterations; x++) {
      let sliceFrom = x * APPENDIX_ITEMS_PER_PAGE;
      let sliceTill = sliceFrom + APPENDIX_ITEMS_PER_PAGE;
      appendixDataPages.push(appendixMainData.slice(sliceFrom, sliceTill));
    }
  }

  // PROCESS GRAPH DATA
  const graphMainData = responseData.graph_data || {};
  let newGraphData = {};

  for (let itemKey in graphMainData) {
    newGraphData[itemKey] = [];

    let boothPair = [];
    const graphItem = graphMainData[itemKey];

    Object.keys(graphItem).forEach((key, idx) => {
      let YEAR_WISE_DATA = [];

      YEARS_LIST.forEach((year) => {
        const yearValue = graphItem[key][year];
        const newYearData = {
          ...yearValue,
          fig: convertGraphDataIntoFig(yearValue.graph_data),
          year: year,
        };
        YEAR_WISE_DATA.push(newYearData);
      });

      boothPair.push({
        ...graphItem[key],
        booth_no: key,
        year_wise_data: YEAR_WISE_DATA,
      });

      if (idx % 2 === 1) {
        newGraphData[itemKey].push(boothPair);
        boothPair = [];
      }
    });
  }

  return {
    AC_NAME: AC_NAME,
    summary_data_pages: summaryDataPages,
    index_data_pages: indexDataPages,
    appendix_data_pages: appendixDataPages,
    COMPARE_TYPE: payload.compare_type,
    graph_data: newGraphData,
    YEARS_LIST: YEARS_LIST,
    GRAPH_FORMAT: GRAPH_FORMAT,
  };
}

module.exports = modelData;
