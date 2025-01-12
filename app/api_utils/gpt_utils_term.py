from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_term_definition(term: str) -> str:
    """
    Fetches a concise definition for a given term, which could be a technical term,
    slang, or internet jargon. Returns a 2-3 sentence explanation.
    """
    prompt = f"""
    Provide a concise 2-3 sentence definition of the following term:
    ---
    Term: {term}
    ---
    The term could be a technical term, slang, or internet jargon. The definition should be clear, precise, 
    and suitable for someone seeking to understand the term's meaning or context.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that provides clear and concise definitions for various terms, including technical terms, slang, and internet jargon."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        definition = response.choices[0].message.content.strip()
        return definition
    except Exception as e:
        print(f"Error fetching definition for {term}: {e}")
        return f"Could not fetch definition for {term}."

if __name__ == "__main__":
    term = input("Enter a term: ")
    definition = get_term_definition(term)
    print(f"\nDefinition for {term}:\n{definition}")