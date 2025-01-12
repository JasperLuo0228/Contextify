from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def extract_entities_with_gpt(transcription: str) -> str:
    """
    Uses GPT-4o to extract entities from the transcription text.
    """
    prompt = f"""
    The following is a transcription text:
    ---
    {transcription}
    ---
    Please extract the following information:
    - Names of people
    - Company names
    - Course names
    - Technical terms

    Format the output as follows:
    Names: [name1, name2, ...]
    Companies: [company1, company2, ...]
    Courses: [course1, course2, ...]
    Technical terms: [term1, term2, ...]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant that helps extract entity information from text."},
                {"role": "user", "content": prompt}
            ]
        )
        print("[DEBUG] Full response:", response)
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error during GPT processing: {e}")
        return "Error: Could not extract entities"