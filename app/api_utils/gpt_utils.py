from dotenv import load_dotenv
import os
import re
from word2number import w2n
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MAJOR_MAP = {
    "Anthorpology": "ANTH",
    "Art": "ART",
    "Asian American Studies": "AS AM",
    "Bioengineering": "BIOE",
    "Black Studies": "BL ST",
    "Chemical Engineering": "CH E",
    "Chemistry and Biochemistry": "CHEM",
    "Chicana and Chicano Studies": "CH ST",
    "Classics": "CLASS",
    "Greek": "GREEK",
    "Latin": "LATIN",
    "Communication": "COMM",
    "Comparative Literature": "C LIT",
    "Computer Science": "CMPSC",
    "Conseling, Clinical & School Psychology": "CNCSP",
    "Biology": "BIOL",
    "Mathematics": "MATH",
    "Music": "MUS",
    "Physics": "PHYS",
    "Earth Science": "EARTH",
    "Chinese": "CHIN",
    "East Asian Language & Cultural Studies": "EACS",
    "Japanese": "JAPAN",
    "Korean": "KOR",
    "Ecology,Ecology&Marine Biology": "EEMB",
    "Economy": "ECON",
    "Education": "ED",
    "Electrical and Computer Engineering": "ECE",
    "English": "ENGL",
    "Environmental Science & Management": "ESM",
    "Environmental Studies": "ENV",
    "Exercise": "ES",
    "Feminist Studies": "FEMST",
    "File and Media Studies": "FAMST",
    "French": "FR",
    "Italian": "ITAL",
    "Geography": "GEOG",
    "Germanic and Slavic Studies": "GER",
    "Global Studies": "GLOBL",
    "History": "HIST",
    "History of Art": "ARTHI",
    "Interdisciplinary": "INT",
    "Quantitative Biosciences": "IQB",
    "Linguistics": "LING",
    "Marine Science": "MARSC",
    "Materials": "MATRL",
    "Mechanical Engineering": "ME",
    "Media Art & Technology": "MAT",
    "Military Science": "MS",
    "Molecular, Celluar & Develop, Biology": "MCDB",
    "Philosophy": "PHIL",
    "Astronomy": "ASTRO",
    "Political Science": "POL S",
    "Psychology": "PSY",
    "Religious Studies": "RG ST",
    "Sociology": "SOC",
    "Portuguese": "PORT",
    "Spanish": "SPAN",
    "Statistics": "PSTAT",
    "Technology Management Program": "TMP",
    "Dance": "DANCE",
    "Theater": "THTR",
    "Writing": "WRIT"
}

def extract_entities_with_gpt(transcription: str) -> dict:
    """
    Uses GPT to extract entities from the transcription text.
    Returns a Python dictionary with these keys:
      - "Names"
      - "Companies"
      - "Courses"
      - "Terms"
    """
    major_prompt = "\n".join([f"{major}: {short}" for major, short in MAJOR_MAP.items()])
    
    prompt = f"""
    The following is a transcription text:
    ---
    {transcription}
    ---
    Please extract the following information:
    - Names of notable people (famous figures only)
    - Company names
    - Course names (must include numbers or letter-number combinations, e.g., CS9 or Statistics 160A)
    - Terms (including technical terms, slang, and internet jargon)
    - For technical terms, it should be complex enough like amino acids or quantum computing, instead of words like scientist

    Notes:
    - Use the following major to course prefix mapping for converting course names to standard formats:
    {major_prompt}
    - If a course name contains words like "one thirty", convert it to numerical format (e.g., 130).
    - Only include valid course names that have numbers. Ignore general mentions like "Computer Science" without a number.
    - Format the output as follows:
    Names: [name1, name2, ...]
    Companies: [company1, company2, ...]
    Courses: [course1, course2, ...]
    Technical terms: [term1, term2, ...]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that helps extract entity information from text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_output = response.choices[0].message.content
        print("[DEBUG] Raw GPT output:", raw_output)

        processed_dict = process_output_as_dict(raw_output)
        return processed_dict
    except Exception as e:
        print(f"Error during GPT processing: {e}")
        return {
            "Names": [],
            "Companies": [],
            "Courses": [],
            "Technical terms": []
        }

def process_output_as_dict(raw_output: str) -> dict:
    """
    Parses the GPT output string and returns a dictionary:
    {
      "Names": [...],
      "Companies": [...],
      "Courses": [...],
      "Technical terms": [...]
    }
    Courses are processed for standard formatting.
    """
    names_str = extract_bracketed_list(raw_output, r"Names:\s*\[(.*?)\]")
    companies_str = extract_bracketed_list(raw_output, r"Companies:\s*\[(.*?)\]")
    courses_str = extract_bracketed_list(raw_output, r"Courses:\s*\[(.*?)\]")
    technical_str = extract_bracketed_list(raw_output, r"Technical terms:\s*\[(.*?)\]")

    names_list = parse_list_items(names_str)
    companies_list = parse_list_items(companies_str)
    course_list = parse_list_items(courses_str)
    technical_list = parse_list_items(technical_str)

    standardized_courses = [
        convert_course_format(course.strip()) for course in course_list if course.strip()
    ]

    return {
        "Names": names_list,
        "Companies": companies_list,
        "Courses": standardized_courses,
        "Technical terms": technical_list
    }

def extract_bracketed_list(text: str, pattern: str) -> str:
    """
    Extracts the contents of a bracketed list (e.g., Names: [Alice, Bob]).
    Returns the matched string without the brackets, or an empty string.
    """
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def parse_list_items(items_str: str) -> list:
    """
    Splits a comma-separated string into a list of items.
    Returns an empty list if the string is empty.
    """
    if not items_str:
        return []
    return [item.strip() for item in items_str.split(",") if item.strip()]

def convert_course_format(course_name: str) -> str:
    """
    Converts course names to standardized format based on MAJOR_MAP.
    Also handles text-to-number conversion (e.g., 'one thirty' -> '130').
    """
    course_name = convert_text_to_number(course_name)
    match = re.match(r"(.+?)\s*(\d+[A-Za-z]*)", course_name, re.IGNORECASE)
    if match:
        major, course_number = match.groups()
        major_cleaned = major.strip()
        major_short = MAJOR_MAP.get(major_cleaned, major_cleaned.upper())
        return f"{major_short}{course_number}"
    return course_name

def convert_text_to_number(text: str) -> str:
    """
    Attempts to convert textual numbers into digits.
    If conversion fails, returns the original text.
    """
    try:
        words = text.split()
        converted_tokens = []
        for word in words:
            if re.match(r"^[a-zA-Z]+$", word):
                converted_tokens.append(str(w2n.word_to_num(word)))
            else:
                converted_tokens.append(word)
        return "".join(converted_tokens)
    except ValueError:
        return text