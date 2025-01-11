from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_entities_with_gpt(transcription: str) -> str:
    """
    Uses GPT-3.5 to extract entities from the transcription text.
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are an assistant that helps extract entity information from text."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print(f"Error during GPT processing: {e}")
        return "Error: Could not extract entities"
