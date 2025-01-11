import requests

def search_wikipedia(query: str, language="en") -> str:
    """
    Searches Wikipedia for a given query and returns the first paragraph of the article.
    """
    url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("extract", "No summary found.")
    except Exception as e:
        print(f"Error during Wikipedia search: {e}")
        return "Error: Could not fetch Wikipedia information."
