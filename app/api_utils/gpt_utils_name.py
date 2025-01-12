from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_person_summary(person_name: str) -> str:
    """
    Uses GPT to fetch a short summary for a given person's name.
    Returns a 2-3 sentence summary similar to Wikipedia's first paragraph.
    """
    prompt = f"""
    Provide a 2-3 sentence summary about the following individual:
    ---
    Name: {person_name}
    ---
    The summary should be concise and provide relevant information about the person, similar to the first paragraph on their Wikipedia page.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that provides concise summaries of well-known individuals."
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
        print(f"Error fetching summary for {person_name}: {e}")
        return f"Could not fetch summary for {person_name}."

if __name__ == "__main__":
    name = input("Enter the name of a person: ")
    summary = get_person_summary(name)
    print(f"\nSummary for {name}:\n{summary}")