import json

with open('questions.json', 'r') as file:
    data = json.load(file)

questions = data['questions']
unique_questions = {q['question_text']: q for q in questions}.values()

if len(questions) != len(unique_questions):
    print("Duplicates found in the JSON file.")
else:
    print("No duplicates in the JSON file.")