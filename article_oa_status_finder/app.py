# app.py

import streamlit as st
import re
from build_articles_oa_overview import build_articles_oa_overview

st.set_page_config(page_title="Open Access Dashboard", page_icon=":unlock:", layout="centered", menu_items={
       'About': "The Open Access Dashboard retrieves a list of your publications from your ORCID profile. For each publication with a DOI, it determines the OA status and journal-specific OA options. Data is from ORCID, Unpaywall, and JISC Open Policy Finder."
    }) 
st.title("Open Access Dashboard")
orcid_input = st.text_input("Enter your ORCID:")


if orcid_input:
    # ORCID validation
    orcid_pattern = r'^[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}$'
    if not re.match(orcid_pattern, orcid_input):
        st.error("Invalid ORCID format. Please use the format XXXX-XXXX-XXXX-XXXX.")
        st.stop()
        
    # Spinner to show while fetching data
    with st.spinner('Loading...'):
        data = build_articles_oa_overview(orcid_input)

    if not data.empty:
        st.header(f"{data.iloc[0]['Author']}'s Publications")
        
        oa_status_options = ["All", "Open Access", "Closed Access"]
        oa_status_selection = st.segmented_control(
        "View publications by open access status:", oa_status_options, selection_mode="single", default="All")
        if oa_status_selection == "Open Access":
            data = data[data['OA Status'] == True]
        elif oa_status_selection == "Closed Access":
            data = data[data['OA Status'] == False]
        
        #Blank space
        st.markdown('##')
        
        # --- MODIFIED PART ---
        # No more columns, just a single loop
        for index, row in data.iterrows():
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
                DOI: [{row['DOI']}](https://doi.org/{row['DOI']})
                ''' 
                st.markdown(multi)

                # # Display journal permissions inside the container
                journal_permissions = row['Journal Permissions']
                journal_permissions.reverse()

                if row['OA Status'] is False:  
                    if journal_permissions:
                        st.markdown("**How to Make This Open Access:**")
                        for perm in journal_permissions:
                            
                            #Logic for oa options panels
                            if perm['additional_oa_fee'] =='Yes':
                                oa_fee_txt = "A fee is required."
                            else:
                                oa_fee_txt = "No fee required."
                            
                            if perm['embargo_period'] == 'None':
                                embargo_txt = "You can make it open access immediately."
                            else:
                                embargo_txt = f"You can make it open access after an embargo period of {perm['embargo_period']}."

                            if perm['deposit_locations'] != 'None':
                                location_txt = f"**Where you can deposit it:** {perm['deposit_locations']}."
                            else: 
                                location_txt = 'No specific deposit locations mentioned.'

                            if perm['named_repositories'] != 'None':
                                named_repo_txt = f"**Permitted repositories:** {perm['named_repositories']}."
                            else:
                                named_repo_txt = ''
                            
                            with st.expander(f"**{perm['version']} Version**"):
                                
                                details = []
                                details.append(f"- **Cost:** {oa_fee_txt}")
                                details.append(f"- **Embargo:** {embargo_txt}")
                                if location_txt and location_txt != 'No specific deposit locations mentioned.':
                                    details.append(f"- {location_txt}")
                                if named_repo_txt:
                                    details.append(f"- {named_repo_txt}")
                            
                                final_text = "\n".join(details)
                                st.write(final_text)
                    else:
                        st.markdown("*No open access options found.*")
                else:
                    st.markdown("")
                    
    else:
        st.error("*No publications found for the provided ORCID.*")