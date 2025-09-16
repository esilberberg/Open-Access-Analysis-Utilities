"""
This script determines the open access statuses of an author's articles listed on their ORCID record.
Articles and their DOIs are collected from the ORCID API by searching the author's ORCID.
The OA status is determined by searching an article's DOI on the Unpaywall API.
Journal OA permissions are retrieved from the JISC Open Policy Finder API.
"""

import requests
import json
import pandas as pd

def build_articles_oa_overview(orcid):
    """
    Retrieves and processes article information for a given ORCID,
    including current open access status and green OA permissions per associated journal.

    Args:
        orcid (str): The ORCID of the author.

    Returns:
        pandas.DataFrame: A DataFrame containing the processed article data.
                          Returns an empty DataFrame if no data is found.
    """

    full_article_information = []

    def get_orcid_data(orcid):
        """
        Retrieves an author's public ORCID record by searching their ORCID on the ORCID API.
        """
        api_endpoint = f'https://pub.orcid.org/v3.0/{orcid}/record'
        headers = {"Accept": "application/vnd.orcid+json"}

        try:
            response = requests.get(api_endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    def find_author_name(record_data):
        """
        Retrieves the author's full name from their ORCID record.
        """
        try:
            author = record_data.get('person', {})
            name = author.get('name', {})
            given_name = name.get('given-names', {}).get('value', '')
            family_name = name.get('family-name', {}).get('value', '')
            return f"{given_name} {family_name}".strip()
        except (KeyError, TypeError):
            return 'Name not found'

    def find_works(record_data):
        """
        Retrieves list of works from an author's ORCID record.
        """
        works_list = []
        try:
            activities = record_data.get('activities-summary', {})
            works_summary = activities.get('works', {})
            groups = works_summary.get('group', [])
            for group in groups:
                works = group.get('work-summary', [])
                works_list.extend(works)
        except (KeyError, TypeError) as e:
            print(f"Error parsing works data: {e}")
        return works_list

    def find_doi(external_ids):
        """
        Retrieves the DOI from *external-id*, which is a list of dictionaries.
        """
        if isinstance(external_ids, dict):
            external_id_list = external_ids.get('external-id', [])
            for ext_id in external_id_list:
                if ext_id.get('external-id-type') == 'doi':
                    return ext_id.get('external-id-value')
        return 'No DOI'

    def get_unpaywall_data(doi):
        """
        Retrieves information for an article by searching its DOI on Unpaywall.
        """
        api_endpoint = f'https://api.unpaywall.org/v2/{doi}?email=test@college.edu'
        try:
            response = requests.get(api_endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    with open('api-jisc.txt') as f:
            api_jisc = f.read()

    def get_jisc_data(issn):
        api_endpoint = f'https://v2.sherpa.ac.uk/cgi/retrieve_by_id?item-type=publication&api-key={api_jisc}&format=Json&identifier={issn}'
        try:
            response = requests.get(api_endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    # ----------- Start of logic -----------
    orcid_record = get_orcid_data(orcid)

    if not orcid_record:
        print("Could not retrieve ORCID record.")
        return pd.DataFrame()
    
    author_name = find_author_name(orcid_record)
    works = find_works(orcid_record)
    
    if not works:
        print(f"\nNo works found for {author_name}.")
        return pd.DataFrame()
    
    for work in works:
        title = work.get('title', {}).get('title', {}).get('value', 'No title')
        year = work.get('publication-date', {}).get('year', {}).get('value', 'No year')
        journal = work.get('journal-title', {}).get('value', 'No journal') if work.get('journal-title') else 'No journal'
        pub_type = work.get('type', {})
        pub_type = pub_type.replace('-', ' ').title()
        doi = find_doi(work.get('external-ids', {}))
        
        is_oa = 'Unknown'
        issn_l = 'No ISSN-L'
        journal_permissions = []

        if doi != 'No DOI':
            unpaywall_data = get_unpaywall_data(doi)
            if unpaywall_data:
                is_oa = unpaywall_data.get('is_oa', False)
                issn_l = unpaywall_data.get('journal_issn_l', 'No ISSN-L')

            if issn_l != 'No ISSN-L':
                jisc_data = get_jisc_data(issn_l)
                if jisc_data and jisc_data.get('items'):
                        # Check if 'publisher_policy' exists and is not empty
                        if jisc_data['items'][0].get('publisher_policy'):
                            permitted_oa_list = jisc_data['items'][0]['publisher_policy'][0].get('permitted_oa', [])
                            for policy in permitted_oa_list:  
                                article_version = policy.get('article_version', ['Unknown'])[0] if policy.get('article_version') else 'Unknown'   
                                oa_fee = policy.get('additional_oa_fee', 'Unknown')
                                embargo = policy.get('embargo')
                                if embargo:
                                    embargo_amount = embargo.get('amount', 'N/A')
                                    embargo_units = embargo.get('units', 'N/A')
                                    embargo_text = f"{embargo_amount} {embargo_units}"
                                else:
                                    embargo_text = 'None'
                                
                                location_data = policy.get('location', {})
                                location_phrases = location_data.get('location_phrases', [])
                                location_names = [loc.get('phrase', 'Unknown') for loc in location_phrases]
                                named_repos = 'None'
                                if 'Named Repository' in location_names:
                                    named_repos = location_data.get('named_repository', {})
                                    named_repos = ', '.join(named_repos)
                                locations = ', '.join(location_names)

                                permission_dict = {
                                    'version': article_version.title(),
                                    'additional_oa_fee': oa_fee.title(),
                                    'embargo_period': embargo_text,
                                    'deposit_locations': locations,
                                    'named_repositories': named_repos
                                }
                        
                                journal_permissions.append(permission_dict)
                                
            row_data = {
                    'ORCID': orcid,
                    'Author': author_name,
                    'DOI': doi,
                    'Article': title,
                    'Year': year,
                    'Publication Type': pub_type,
                    'Journal': journal,
                    'ISSN-L': issn_l,
                    'OA Status': is_oa,
                    'Journal Permissions': journal_permissions
                }
        
            full_article_information.append(row_data)


    df = pd.DataFrame(full_article_information, columns=['ORCID', 'Author', 'DOI', 'Article', 'Year', 'Publication Type', 'Journal', 'ISSN-L', 'OA Status', 'Journal Permissions'])
    return df