import json
import requests
import os
from app import db, app
from app.models import Questions

def load_questions_from_json_url(url):
    """
    Loads questions from a JSON file hosted at a given URL and
    adds them to the database.
    """
    # Get the Hugging Face token from an environment variable for security
    hf_token = os.environ.get("HUGGINGFACE_TOKEN")

    if not hf_token:
        print("Error: HUGGINGFACE_TOKEN environment variable is not set.")
        print("Please set your Hugging Face token before running this script.")
        return

    headers = {"Authorization": f"Bearer {hf_token}"}

    print("Attempting to download questions from the provided URL...")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        print("Download successful. Starting to process questions...")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file from {url}: {e}")
        return

    for item in data:
        existing_q = Questions.query.get(item.get('id'))
        if existing_q:
            print(f"Skipping question with ID {item['id']} as it already exists.")
            continue
            
        new_question = Questions(
            id=item.get('id'),
            question=item.get('question'),
            choices=json.dumps(item.get('choices')),  # Store choices as a JSON string
            answer=item.get('answer'),
            explanation=item.get('explanation'),
            topic=item.get('topic'),
            difficulty=item.get('difficulty'),
            source=item.get('source')
        )
        db.session.add(new_question)
        print(f"Added question with ID {item['id']}")

    db.session.commit()
    print("All new questions successfully committed to the database.")

if __name__ == '__main__':
    # Add a with block to create an application context
    with app.app_context():
        # The code inside this block can now access the database
        # huggingface_url = "https://huggingface.co/datasets/TechTCM/TCMBenchmark/resolve/main/Full_TechTCM_Evaluation_Set.json"
        # huggingface_url = "https://huggingface.co/datasets/TechTCM/TCMBenchmark/resolve/main/multi_single_mix.json"
        # huggingface_url = "https://huggingface.co/datasets/TechTCM/TCMBenchmark/resolve/main/10000_items.json"
        
        #huggingface_url = "https://huggingface.co/datasets/TechTCM/TCMBenchmark/resolve/main/5000_stratified_items.json"
        #huggingface_url = "https://huggingface.co/datasets/TechTCM/TCMBenchmark/resolve/main/20_stratified_items.json"
        
        huggingface_url = "https://huggingface.co/datasets/TechTCM/TCMBenchmark/resolve/main/6000_stratified_items.json"
        
        load_questions_from_json_url(huggingface_url)
