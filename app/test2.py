import unittest
from api_utils.wikipedia_utils import search_wikipedia

class TestWikipediaSearch(unittest.TestCase):

    def test_search_real_query(self):
    
        query = "C++ (programming language)"
        result = search_wikipedia(query)

        print(f"\n『{query}』：\n{result}\n")
        self.assertNotEqual(result, "No summary found.")
        self.assertNotIn("Error", result)

    def test_search_needs_company_suffix(self):
        query = "Amazon"
        result = search_wikipedia(query)

        print(f"\n『{query}』：\n{result}\n")

        self.assertNotEqual(result, "No summary found.")
        self.assertNotIn("Error", result)

    def test_search_non_existing_page(self):
        query = "asdkjashdjkashdkjahsdkjh"
        result = search_wikipedia(query)

        print(f"\n『{query}』：\n{result}\n")

        self.assertEqual(result, "Error: Could not fetch Wikipedia information.")

    def test_search_short_query_no_company_suffix(self):
        query = "zzzzzzzzzzzz" 
        result = search_wikipedia(query)

        print(f"\n『{query}』（(company)）：\n{result}\n")

        self.assertEqual(result, "Error: Could not fetch Wikipedia information.")
    def test_search_valid_company(self):
        query = "Amazon"
        result = search_wikipedia(query)

        print(f"\n『{query}』：\n{result}\n")

        self.assertNotEqual(result, "No summary found.")
        self.assertNotIn("Error", result)

if __name__ == "__main__":
    unittest.main()