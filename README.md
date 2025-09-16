# AI-Assisted Open Access Policy Finder

## Overview
The `ai_assisted_oa_policy_finder.py` script is a Python tool designed to automate the process of analyzing open access (OA) policies for a list of academic citations. It leverages the power of AI to extract journal names and then queries the JISC Open Policy Finder API to retrieve detailed OA policies.

This script is particularly useful for researchers, librarians, and students who need to understand the publication rights and open access requirements for their work.

## How it works

- **Extracts Journal Names:** The script uses [Google's Gemini LLM API](https://ai.google.dev/gemini-api/docs) to analyze a list of citations provided in a spreadsheet. It isolates the journal name from each citation, handling abbreviations and other variations.

- **Queries OA Policies:** Using the extracted journal names, the script calls the [JISC Open Policy Finder API](https://www.sherpa.ac.uk/api/) to retrieve OA policies for each journal.

- **Generates a Report:** The script compiles all the information into a single, text file, `QCL_CV_OA_Report.txt`, which includes details on article versions, embargo periods, fees, and conditions.

## Dependencies
- Google AI Studio API Key
- JISC Open Policy Finder API Key
- Python Libraries:
    - google.generativeai
    - pandas

### Limitations
The accuracy of the information in the final report is dependent on the data provided by the JISC Open Policy Finder.

