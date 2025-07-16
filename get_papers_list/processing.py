# get_papers_list/processing.py

from lxml import etree
from typing import List, Tuple, Optional
import logging
from .models import Author, Paper, FilteredPaper

logger = logging.getLogger(__name__)

# Heuristics for identifying non-academic affiliations
ACADEMIC_KEYWORDS = [
    'university', 'college', 'hospital', 'institute', 'school of', 
    'department of', 'faculty of', 'center for', 'research center'
]
COMPANY_KEYWORDS = [
    'inc', 'ltd', 'gmbh', 'corp', 'pharmaceuticals', 'therapeutics',
    'biopharma', 'biotech', 'diagnostics', 'ventures', 'llc'
]


def _is_non_academic(affiliation: str) -> bool:
    """Determines if an affiliation is non-academic based on keywords."""
    if not affiliation:
        return False
    
    lower_aff = affiliation.lower()
    
    # It is likely a company if it contains a corporate keyword.
    if any(f' {kw}' in lower_aff or f',{kw}' in lower_aff for kw in COMPANY_KEYWORDS):
        return True
        
    # It is likely academic if it contains an academic keyword.
    if any(kw in lower_aff for kw in ACADEMIC_KEYWORDS):
        return False
        
    # If no keywords match, assume it's non-academic (heuristic).
    # This catches smaller companies that don't list a suffix.
    return True

def _parse_publication_date(article_node: etree._Element) -> str:
    """Extracts the publication date from the XML node."""
    pub_date_node = article_node.find(".//PubDate")
    if pub_date_node is not None:
        year = pub_date_node.findtext("Year", "N/A")
        month = pub_date_node.findtext("Month", "N/A")
        day = pub_date_node.findtext("Day", "N/A")
        return f"{year}-{month}-{day}"
    return "No Date Found"

def _find_corresponding_email(author_list_node: etree._Element) -> Optional[str]:
    """Scans author affiliations for an email address."""
    for affiliation in author_list_node.xpath(".//Affiliation/text()"):
        # A simple regex could be more robust, but this is a common pattern.
        parts = [part for part in affiliation.split() if '@' in part]
        if parts:
            email = parts[0].strip('.,;()[]')
            return email
    return None

def parse_pubmed_xml(xml_data: str) -> List[Paper]:
    """Parses the XML response from PubMed efetch into a list of Paper objects."""
    if not xml_data:
        return []

    root = etree.fromstring(xml_data.encode('utf-8'))
    papers = []
    
    for article_node in root.xpath("//PubmedArticle"):
        pmid = article_node.findtext(".//PMID", "N/A")
        title = article_node.findtext(".//ArticleTitle", "No Title Found")
        pub_date = _parse_publication_date(article_node)
        
        authors = []
        author_list_node = article_node.find(".//AuthorList")
        email = None
        if author_list_node is not None:
            email = _find_corresponding_email(author_list_node)
            for author_node in author_list_node.xpath(".//Author"):
                authors.append(
                    Author(
                        last_name=author_node.findtext("LastName"),
                        fore_name=author_node.findtext("ForeName"),
                        initials=author_node.findtext("Initials"),
                        affiliation=author_node.findtext(".//Affiliation"),
                    )
                )

        papers.append(Paper(pmid=pmid, title=title, publication_date=pub_date, authors=authors, corresponding_author_email=email))
    
    logger.info(f"Parsed {len(papers)} paper(s) from XML data.")
    return papers

def filter_papers_by_affiliation(papers: List[Paper]) -> List[FilteredPaper]:
    """
    Filters a list of papers to find those with non-academic authors.
    """
    filtered_list = []
    for paper in papers:
        non_academic_authors = []
        company_affiliations = set()

        for author in paper.authors:
            if author.affiliation and _is_non_academic(author.affiliation):
                author_name = f"{author.fore_name or ''} {author.last_name or ''}".strip()
                if author_name:
                    non_academic_authors.append(author_name)
                    company_affiliations.add(author.affiliation)
        
        if non_academic_authors:
            filtered_list.append(
                FilteredPaper(
                    pubmed_id=paper.pmid,
                    title=paper.title.strip(),
                    publication_date=paper.publication_date,
                    non_academic_authors="; ".join(non_academic_authors),
                    company_affiliations="; ".join(sorted(list(company_affiliations))),
                    corresponding_author_email=paper.corresponding_author_email,
                )
            )
            
    logger.info(f"Found {len(filtered_list)} paper(s) with non-academic authors.")
    return filtered_list