# cli/main.py

import typer
from typing_extensions import Annotated
import logging
import sys
import csv

from get_papers_list import api, processing

app = typer.Typer()

def setup_logging(debug: bool):
    """Configures logging based on the debug flag."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stderr,  # Log to stderr to not interfere with CSV output to stdout
    )

def write_to_csv(data: list, file_path: str = None):
    """Writes the filtered paper data to a CSV file or stdout."""
    if not data:
        logging.info("No data to write.")
        return
        
    # Use the fields from the dataclass as headers
    headers = [
        "PubmedID", "Title", "Publication Date", 
        "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"
    ]
    
    output_target = open(file_path, 'w', newline='', encoding='utf-8') if file_path else sys.stdout
    
    writer = csv.writer(output_target)
    writer.writerow(headers) # Write header [cite: 11]
    
    for paper in data:
        writer.writerow([
            paper.pubmed_id, # [cite: 12]
            paper.title, # [cite: 13]
            paper.publication_date, # [cite: 14]
            paper.non_academic_authors, # [cite: 15]
            paper.company_affiliations, # [cite: 16]
            paper.corresponding_author_email or "N/A", # [cite: 16]
        ])
        
    if file_path:
        output_target.close()
        logging.info(f"Results successfully saved to {file_path}")

@app.command()
def main(
    query: Annotated[str, typer.Argument(help="The full query to search on PubMed.")],
    file: Annotated[
        str,
        typer.Option(
            "-f", "--file",
            help="Specify the filename to save the results. Prints to console if not provided."
        ),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "-d", "--debug",
            help="Print debug information during execution."
        ),
    ] = False,
):
    """
    Fetches research papers from PubMed based on a query, filters for authors
    from pharmaceutical or biotech companies, and returns the results as a CSV.
    """
    setup_logging(debug)
    
    try:
        logging.info("Starting paper retrieval process...")
        # 1. Search for papers
        pmids = api.search_pubmed(query)
        if not pmids:
            logging.warning("No papers found for the given query.")
            typer.echo("No papers found.")
            raise typer.Exit()
            
        # 2. Fetch paper details
        xml_data = api.fetch_paper_details(pmids)
        
        # 3. Parse XML data
        papers = processing.parse_pubmed_xml(xml_data)
        
        # 4. Filter for non-academic affiliations
        filtered_papers = processing.filter_papers_by_affiliation(papers)
        
        # 5. Write output
        if not filtered_papers:
            logging.warning("No papers with non-academic authors found.")
            typer.echo("Found papers, but none matched the non-academic author criteria.")
            raise typer.Exit()

        write_to_csv(filtered_papers, file)

    except requests.exceptions.RequestException as e:
        logging.error(f"An API error occurred: {e}")
        typer.echo(f"Error: Could not connect to PubMed API. Please check your connection.", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=debug)
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()