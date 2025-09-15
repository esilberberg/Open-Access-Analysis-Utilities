# app.py

import streamlit as st
import pandas as pd
from build_articles_oa_overview import build_articles_oa_overview

st.set_page_config(layout="wide") 

st.title('Author\'s Open Access Dashboard')

orcid_input = st.text_input('Enter your ORCID')

if orcid_input:
    # Spinner to show while fetching data
    with st.spinner('Loading...'):
        data = build_articles_oa_overview(orcid_input)

    if not data.empty:
        st.header(f"{data.iloc[0]['Author']}")
        st.write(f"{orcid_input}")
        st.write("---")

        st.subheader("Publications")
        col1, col2 = st.columns(2)

        for index, row in data.iterrows():
            target_column = col1 if index % 2 == 0 else col2
            
            with target_column:
                # A container to group all the content for one article
                with st.container(border=True):
                    st.write(f"Article {index + 1}")
                    st.markdown(f"##### {row['Article']}")
                    st.markdown(f"**Journal:** {row['Journal']}")
                    st.markdown(f"**OA Status:** {'Open Access' if row['OA Status'] else 'Closed Access'}")
                    st.markdown(f"**DOI:** [{row['DOI']}](https://doi.org/{row['DOI']})")

                    # # Display journal permissions inside the container
                    # journal_permissions = row['Journal Permissions']
                    # if journal_permissions:
                    #     st.markdown("**Green OA Permissions:**")
                    #     for permission in journal_permissions:
                    #         st.json(permission, expanded=False) # Start collapsed
                    # else:
                    #     st.markdown("**Green OA Permissions:** Not found")

    else:
        st.error("No articles found for the provided ORCID or an error occurred.")