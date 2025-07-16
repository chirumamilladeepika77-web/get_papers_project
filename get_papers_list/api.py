# get_papers_list/api.py

import requests
from typing import List, Dict, Any
import logging

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
logger = logging.getLogger(__name__)

def search_pubmed(query: str, max_papers: int = 100) -> List[str]:
    """
    Searches PubMed for a query and returns a list of matching PubMed IDs (PMIDs).
    """
    search_url = f"{BASE_URL}esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_papers,
    }
    logger.debug(f"Searching PubMed with URL: {search_url} and params: {params}")
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])
        logger.info(f"Found {len(pmids)} paper(s) for query: '{query}'")
        return pmids
    except requests.exceptions.RequestException as e:
        logger.error(f"PubMed API search failed: {e}")
        raise

def fetch_paper_details(pmids: List[str]) -> str:
    """
    Fetches detailed information for a list of PMIDs from PubMed in XML format.
    """
    if not pmids:
        return ""
    
    fetch_url = f"{BASE_URL}efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    logger.debug(f"Fetching details for {len(pmids)} PMIDs.")
    try:
        response = requests.post(fetch_url, data=params) # Use POST for long lists of IDs
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"PubMed API fetch failed: {e}")
        raise