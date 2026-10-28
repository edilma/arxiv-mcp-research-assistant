import arxiv
import json
import os
from typing import List
import pathlib
#from mcp.server.fastmcp import FastMCPServer
from mcp.server.mcpserver import MCPServer




#where the downloaded papers will be stored
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
PAPER_DIR = PROJECT_ROOT / "papers"


#initialize FastMCPServer
mcp= MCPServer("research")

#The first tool searches for relevant arXiv papers based on a topic and stores the papers' #info in a JSON file (title, authors, summary, paper url and the publication date). The JSON #files are organized by topics in the papers directory. The tool does not download the #papers.
@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic. and store their information in a JSON file.

    Args:
        topic (str): The topic to search for.
        max_results (int): The maximum number of results to return.

    Returns:
        List[str]: A list of paper IDs for the found papers.
    """
    #Use arxiv to find the papers
    client = arxiv.Client(
        page_size=5,
        delay_seconds=3,
        num_retries=3,
    )

    #Search for the most relevant articles matching the queried topic

    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers = client.results(search)
   #create a directory for this topic
    path = PAPER_DIR / topic.lower().replace(" ", "_")
    if not path.exists():
       path.mkdir(parents=True)

    file_path = path / "papers.json"

    #Try to load existing papers info
    try:
        with open(file_path, "r") as jason_file:
            papers_info = json.load(jason_file)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}

    paper_ids = []
    for paper in papers:
        if "paper_ids" not in locals():
            paper_ids = []
        paper_id = paper.get_short_id()
        paper_ids.append(paper_id)
        paper_info = {
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "summary": paper.summary,
            "published": paper.published.isoformat(),
            "updated": paper.updated.isoformat(),
            "pdf_url": paper.pdf_url
        }
        papers_info[paper_id] = paper_info

    #save updated papers info to the JSON file
    with open(file_path, "w") as jason_file:
        json.dump(papers_info, jason_file, indent=4)

    print(f"Saved papers information to {file_path}")

    return paper_ids

# The second tool looks for information about a specific paper across all topic directories inside the papers directory.

@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper across all topic directories inside the papers directory.

    Args:
        paper_id (str): The ID of the paper to search for.

    Returns:
        str: The JSON string containing the paper information if found, otherwise error message.
    """
    for topic_dir in PAPER_DIR.iterdir():
        if topic_dir.is_dir():
            file_path = topic_dir / "papers.json"
            if file_path.exists():
                try:
                    with open(file_path, "r") as jason_file:
                        papers_info = json.load(jason_file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=4)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
    return f"Paper with ID {paper_id} not found."


@mcp.resource("papers://folders")
def get_available_folders() -> str:
    """List topics containing saved paper information."""
    folders = []

    if PAPER_DIR.exists():
        for topic_dir in PAPER_DIR.iterdir():
            if topic_dir.is_dir() and (topic_dir / "papers.json").exists():
                folders.append(topic_dir.name)

    if not folders:
        return "No saved research topics found."

    return "# Available Topics\n\n" + "\n".join(
        f"- {folder}" for folder in sorted(folders)
    )


@mcp.resource("papers://{topic}")
def get_topic_papers(topic: str) -> str:
    """Return the saved research papers for a specific topic."""

    file_path = PAPER_DIR / topic / "papers.json"

    if not file_path.is_file():
        return f"No saved papers found for topic: {topic}"

    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            papers_info = json.load(json_file)

        return json.dumps(papers_info, indent=4)

    except json.JSONDecodeError:
        return f"Error: papers.json for {topic} is invalid."

@mcp.prompt()
def generate_search_prompt(topic: str, num_papers: int = 5) -> str:
    """Generate a prompt for Claude to find and discuss academic papers on a specific topic."""
    return f"""Search for {num_papers} academic papers about '{topic}' using the search_papers tool. Follow these instructions:
    1. First, search for papers using search_papers(topic='{topic}', max_results={num_papers})
    2. For each paper found, extract and organize the following information:
       - Paper title
       - Authors
       - Publication date
       - Brief summary of the key findings
       - Main contributions or innovations
       - Methodologies used
       - Relevance to the topic '{topic}'
    
    3. Provide a comprehensive summary that includes:
       - Overview of the current state of research in '{topic}'
       - Common themes and trends across the papers
       - Key research gaps or areas for future investigation
       - Most impactful or influential papers in this area
    
    4. Organize your findings in a clear, structured format with headings and bullet points for easy readability.
    
    Please present both detailed information about each paper and a high-level synthesis of the research landscape in {topic}."""



if __name__ == "__main__":
    mcp.run(transport="stdio") 