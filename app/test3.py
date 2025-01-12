import unittest
from dotenv import load_dotenv
import os
from api_utils.bing_utils import search_bing_news
load_dotenv()
api_key = os.getenv("BING_API_KEY")

class TestBingNewsAPI(unittest.TestCase):

    def test_valid_news_search(self):
    
        query = "Tiktok"
        count = 5 

        result = search_bing_news(api_key=api_key, query=query, count=count)

        self.assertIn("value", result, "API No return 'value' Paragraphs")
        self.assertGreater(len(result["value"]), 0, "API has no news return")

        for idx, article in enumerate(result["value"], start=1):
            title = article.get("name", "No title")
            description = article.get("description", "No summary")
            image_url = article.get("image", {}).get("thumbnail", {}).get("contentUrl", "No photo")

            print(f"\n【Number {idx} News")
            print(f"Title: {title}")
            print(f"Summary: {description}")
            print(f"Photo: {image_url}\n")


            self.assertIsNotNone(title, f" The {idx} th News has no Summary")
            self.assertIsNotNone(description, f" The {idx} th News has no Summry")
            if image_url != "No Photo":
                self.assertTrue(image_url.startswith("http"), f" The {idx} th News has unavaliable Photo")

    def test_invalid_api_key(self):

        invalid_api_key = "invalid_key"
        result = search_bing_news(api_key=invalid_api_key, query="Technology")

        print(f"\n Error: {result.get('error')}\n")

        self.assertIn("error", result, "didn't catch any API mistakes")
        self.assertTrue(
            "401" in result["error"] or "PermissionDenied" in result["error"],
            "Error doesn't match the expectation"
        )

    def test_empty_query(self):
        result = search_bing_news(api_key=api_key, query="")

        print(f"\nEmpty Research: {result}\n")

        self.assertIn("value", result, "Empty Research didn't return 'value' Paragraphs")
        self.assertEqual(len(result["value"]), 0, "The empty query returned unexpected data.")

if __name__ == "__main__":
    unittest.main()