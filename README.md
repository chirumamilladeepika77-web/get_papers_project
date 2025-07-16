# Get Papers List

This project provides a Python command-line tool to fetch research papers from PubMed based on a user-specified query. It filters the results to identify papers with at least one author affiliated with a pharmaceutical or biotech company and outputs the data to a CSV file or the console.

## Code Organization

The project is structured into two main parts:

1.  **`get_papers_list` (Reusable Module)**: This is the core library responsible for all business logic.
    * `api.py`: Handles all interactions with the PubMed API.
    * `processing.py`: Contains functions for parsing API responses, implementing the filtering logic, and processing data.
    * `models.py`: Defines data structures for type safety and clarity.

2.  **`cli` (Command-Line Program)**: This part provides the user interface.
    * `main.py`: Uses the `typer` library to create a robust CLI that accepts user arguments and calls the `get_papers_list` module to perform the work.

This separation of concerns makes the core logic reusable and easy to test independently of the command-line interface.

## Installation & Setup

This project uses **Poetry** for dependency management.

1.  **Install Poetry:** If you don't have Poetry, follow its [official installation instructions](https://python-poetry.org/docs/#installation).

2.  **Clone the repository:**
    ```bash
    git clone <your-github-repository-url>
    cd get-papers-project
    ```

3.  **Install dependencies:** Run the following command in the project root. Poetry will create a virtual environment and install all necessary packages.
    ```bash
    poetry install
    ```

## How to Execute the Program

The program is run via the `get-papers-list` command, which is made available by Poetry's script management.

**Syntax:**
```bash
poetry run get-papers-list "your pubmed query" [OPTIONS]