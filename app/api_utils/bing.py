from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.getenv("BING_API_KEY")
def search_bing_news(api_key: str, query: str, count: int = 10) -> dict:
    """    
    Parameters:
        api_key (str): The API key for Bing News Search.
        query (str): The search query.
        count (int): The number of news results to fetch (default: 10).
    
    Returns:
        dict: The JSON response from the Bing News API.
    """
    endpoint = "https://api.bing.microsoft.com/v7.0/news/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "count": count}
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()  
        return response.json()
    except Exception as e:
        print(f"Error during Bing News Search API call: {e}")
        return {"error": str(e)}
