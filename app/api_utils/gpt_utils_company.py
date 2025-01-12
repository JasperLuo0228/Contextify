from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_company_summary(company_name: str) -> str:
    """
    Uses GPT to generate a concise 2-3 sentence summary for a company.
    If Wikipedia fails, this method provides a fallback.
    
    Args:
        company_name (str): The name of the company to summarize.
    
    Returns:
        str: A concise 2-3 sentence summary of the company.
    """
    prompt = f"""
    Provide a concise 2-3 sentence summary for the following company:
    ---
    Name: {company_name}
    ---
    The summary should include its primary industry, key achievements, or global significance, similar to a Wikipedia introduction.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that provides concise summaries of companies."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"Error generating summary for {company_name}: {e}")
        return f"Could not fetch summary for {company_name}."

if __name__ == "__main__":
    name = input("Enter the name of a company: ")
    summary = get_company_summary(name)
    print(f"\nSummary for {name}:\n{summary}")