from api_utils.gpt_utils import extract_entities_with_gpt

def main():
    transcription = """
    John Doe works as a software engineer at Tesla. He graduated from UC Santa Barbara last year, where he completed courses such as Computer Science One Thirty and Statistics One Twenty. Recently, he discussed the impact of transformer models on natural language processing with his boss, Elon Musk.
    """

    print("[INFO] Testing GPT-4o entity extraction with the following transcription:")
    print(transcription)

    extracted_entities = extract_entities_with_gpt(transcription)
    print("\n[RESULT] Extracted Entities:")
    print(extracted_entities)

if __name__ == "__main__":
    main()