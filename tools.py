import os, re
from crewai.tools import tool
from firecrawl import FirecrawlApp


@tool
def web_search_tool(query: str):
    """
    Web Search Tool.
    ...
    """
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    try:
        # Expected to return a list/iterable of tuples
        raw_response = app.search(
            query=query,
            limit=5,
            scrape_options={
                "formats": ["markdown"],
            },
        )
    except Exception as e:
        return f"Error during Firecrawl search: {e}"

    if not raw_response:
        return "Search completed, but no results were returned."

    # Extract the list of results, which is expected to be the second element (index 1) 
    # of the first tuple returned by the Firecrawl client in your environment.
    try:
        results_list = raw_response[0][1]
    except Exception as e:
        return f"Error: Could not extract the results list from the raw response structure. Error: {e}"


    if not results_list:
        return "Search completed, but the extracted list of results was empty."

    cleaned_chunks = []

    # Iterate over the extracted list of Documents/SearchResultWeb objects
    for result_obj in results_list:
        
        # Check if the result is a Document (which contains markdown, url, and title in metadata)
        if hasattr(result_obj, 'metadata'):
            # The URL and Title are inside the 'metadata' attribute
            title = result_obj.metadata.title
            url = result_obj.metadata.url
            # The markdown content is directly on the object
            markdown = result_obj.markdown
            
        # Check if the result is a simple SearchResultWeb object (which might not have full markdown)
        elif hasattr(result_obj, 'url'):
            # Use title, url, and description/placeholder for markdown
            title = result_obj.title
            url = result_obj.url
            markdown = result_obj.description or "Full content not scraped (Result is SearchResultWeb)."
        
        else:
            # Skip any malformed or unexpected result types
            continue 

        # Final cleaning and structuring
        title = title.replace('\xa0', ' ').strip() if title else "No Title"
        url = url.strip() if url else "No URL"
        markdown = markdown if markdown else ""
        
        # Your existing cleaning logic
        cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)

        cleaned_result = {
            "title": title,
            "url": url,
            "markdown": cleaned,
        }

        cleaned_chunks.append(cleaned_result)

    return cleaned_chunks