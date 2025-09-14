# Open Access Analysis Utilities
This repository includes two scripts that analyze the open access (OA) policies of scholarly publications in the hope of encouraging researchers and authors to self-deposit their published work in institutional repositories. 

## AI Journal OA Policy Finder
When evaluating the Green OA (self-archiving) potential of a researcher's publications, one approach is to analyze the OA policies of the journals where their articles were published. 

As citation formatting on a CV can be inconsistent, this script uses [Google's Gemini LLM API](https://ai.google.dev/gemini-api/docs) to extract the correct journal name from each citation. It then queries the [JISC Open Policy Finder API](https://www.sherpa.ac.uk/api/) to retrieve each journal's specific OA policies, and produces a report detailing which publications are eligible for self-archiving.

### Dependencies
API keys for the Gemini and JISC Open Policy Finder.

## Article OA Status Finder
This script automates the process of generating a report on a researcher's publications and their OA status. The script retrieves a list of a researcher's published works and their DOIs by searching an author's ORCID on the [ORCID API](https://info.orcid.org/what-is-orcid/services/public-api/). It then queries the [Unpaywall API](https://unpaywall.org/products/api) to determine the OA status of each article, and uses the [JISC Open Policy Finder API](https://www.sherpa.ac.uk/api/) to find detailed self-archiving permissions from the relevant journals. The final output is a comprehensive report on the author's publications, detailing their OA status and the permissions for each journal.

### Dependencies
API key for JISC Open Policy Finder.
