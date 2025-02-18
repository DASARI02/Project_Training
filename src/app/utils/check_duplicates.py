import json

def check_duplicates(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        questions = data['questions']
        unique_questions = {q['question_text']: q for q in questions}.values()

        if len(questions) != len(unique_questions):
            print("Duplicates found in the JSON file.")
        else:
            print("No duplicates in the JSON file.")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
