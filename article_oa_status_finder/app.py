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
                # A container for all the content for one article
                with st.container(border=True):
                
                    st.write()
                    st.markdown(f"##### {row['Article']}")
                
                    if row['OA Status']:
                        st.badge("Open Access", icon=":material/check:", color="green")
                    else: 
                        st.badge("Closed Access", icon="⚠️", color="orange")

                    if row['Journal'] != 'No journal':
                        journal_info = f"{row['Journal']}"
                    else: journal_info = ''

                    multi = f'''
                    {journal_info}  
                    {row['Year']}  |  {row['Publication Type']}  
                    **DOI:** [{row['DOI']}](https://doi.org/{row['DOI']})
                    ''' 
                    st.markdown(multi)

                    # # Display journal permissions inside the container
                    journal_permissions = row['Journal Permissions']
                    journal_permissions.reverse()
                    if row['OA Status'] is False:  
                        if journal_permissions:
                            st.markdown("**Open Access Options:**")
                            for perm in journal_permissions:
                                with st.expander(f"{perm['version']} Manuscript"):
                                    st.write(f'''
                                    **Fee Required**: {perm['additional_oa_fee']}  
                                    **Embargo Period**: {perm['embargo_period']}  
                                    **May Deposit in**: {perm['deposit_locations']}  
                                    **Permitted Repositories**: {perm['named_repositories']}  
                                    ''')
                        else:
                            st.markdown("No open access options found.")
                    else:
                        st.markdown("")
                        

    else:
        st.error("No articles found for the provided ORCID or an error occurred.")