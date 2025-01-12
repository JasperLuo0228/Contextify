import requests
import re

def search_wikipedia(query: str, language="en") -> str:
    """
    Searches Wikipedia for a given query and returns the first two sentences of the article.
    If the query fails and seems like a company name, it retries by appending '(company)'.
    """
    
    def is_valid_for_company_suffix(query):
        return len(query) > 3 and any(c.isalpha() for c in query)

    def fetch_summary(search_term):
        url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{search_term}"
        try:
            response = requests.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            if data.get("type") == "disambiguation":
                return "DISAMBIGUATION"

            return data.get("extract", None)
        except Exception as e:
            print(f"Error during Wikipedia search for '{search_term}': {e}")
            return None
        
    summary = fetch_summary(query)

    if summary == "DISAMBIGUATION":
        print(f"『{query}』 has disambiguation，try to search '{query} (company)'...")
        summary = fetch_summary(f"{query} (company)")

    if summary is None and is_valid_for_company_suffix(query):
        print(f"Could not find'{query}', Try to research'{query} (company)'...")
        summary = fetch_summary(f"{query} (company)")

    if summary is None:
        return "Error: Could not fetch Wikipedia information."

    sentences = re.split(r'(?<=[.!?。！？‥])\s+', summary)
    first_two_sentences = ' '.join(sentences[:1])

    return first_two_sentences