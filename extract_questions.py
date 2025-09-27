import sqlite3
import json
import os
import ast 
from collections import defaultdict

# --- Configuration ---
DATABASE_PATH = 'app.db'
EXTRACTED_JSON_PATH = 'extracted_questions.json'
FLAGGED_JSON_PATH = 'flagged_questions.json'

# Simplified Chinese category map
CATEGORY_MAP = {
    "1": "【中醫基礎理論】",
    "2": "【中醫經典文獻】",
    "3": "【診斷與辨證學】",
    "4": "【經絡與針灸學】",
    "5": "【中藥本草學】",
    "6": "【中醫內科學】（含婦科兒科神志病）",
    "7": "【中醫外科學】（含皮膚科、傷科）",
    "8": "【中醫五官科學】（含眼耳鼻喉眼）",
    "9": "【中醫法規】",
    "10": "【其他】"
}

def safe_literal_load(data_str, normalize_to_list=False):
    """
    Attempts to parse a string as JSON or Python literal.
    If normalize_to_list is True, any resulting single string ('B') is wrapped
    in a list (['B']) for consistent output formatting.
    """
    if not data_str:
        return []
    
    result = None
    
    # print("datastring: ", data_str)
    if data_str in ["A", "B", "C", "D", ]:
        # print("beofre datastring: ", data_str)
        data_str = json.dumps([data_str])
        # print("after datastring: ", data_str)
    try:
        # Try 1: Standard JSON decoding (e.g., '["A", "B"]')
        result = json.loads(data_str)
        # print("result in try1: ", result ) # this works for categories and multichoice?
    except json.JSONDecodeError:
        try:
            # Try 2: Safe Python literal evaluation (e.g., "['A', 'B']" or simple string "B")
            result = ast.literal_eval(data_str)
            # print("result in try2: ", result ) # never runs
        except (ValueError, SyntaxError, TypeError):
            # If all else fails, treat as failure
            return []
    
    # --- Normalization for Selected Choices ---
    if normalize_to_list:
        # print("in normalize to list: ", json.dumps(result))
        # If the result is a simple string (like 'B'), wrap it in a list ['B'].
        # no this never runs
        if isinstance(result, str):
            return json.dumps(result)
        # If it's a list already (multi-choice), return it.
        if isinstance(result, list):
            return result
        # Anything else is treated as empty/invalid for choices
        return []

    # Default return if not normalizing (e.g., for base question choices)
    return result

def process_and_export_data():
    """
    Connects to the database, aggregates ALL raw interaction data per question/user,
    and exports questions to two JSON files based on the new structure.
    """
    conn = None
    try:
        # Step 1: Connect and fetch base questions
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Fetch all base question data
        cursor.execute("SELECT question_id, question, choices, answer, explanation, topic, source FROM questions")
        base_questions = {row[0]: {
            "id": row[0],
            "question": row[1],
            "choices": json.loads(row[2]),
            "answer": row[3],
            "explanation": row[4],
            "topic": row[5],
            "source": row[6],
            # Initialize new fields to empty dictionaries as per request
            "difficulty": {},
            "categories": {},
            "selected_choices": {}
        } for row in cursor.fetchall()}

        # Dictionary to hold all raw interactions keyed by question_id
        raw_interactions = defaultdict(lambda: {
            "difficulty": {},
            "categories": {},
            "selected_choices": {},
            "is_flagged": False
        })
        
        flagged_question_ids = set()

        # Step 2: Fetch ALL user interactions, including user_id and selected_choices
        cursor.execute(
            """
            SELECT user_id, question_id, selected_difficulty, selected_category, is_flagged, selected_choices 
            FROM user_interactions
            """
        )
        interactions = cursor.fetchall()

        # Step 3: Aggregate raw data from interactions
        for interaction in interactions:
            user_id, q_id, diff, cat_str, is_flagged, selected_choices_str = interaction
            
            # Skip if the base question data doesn't exist (e.g., orphaned interaction)
            if q_id not in base_questions:
                continue

            # Convert user_id to string for consistent JSON keying
            user_key = str(user_id)
            
            # --- 1. Difficulty (Store raw user choice) ---
            if diff is not None:
                raw_interactions[q_id]["difficulty"][user_key] = diff
            
            # --- 2. Selected Choices (Store raw user answer) ---
            # IMPORTANT: We use normalize_to_list=True here to ensure single choices ('B') become ['B']
            choices_data = safe_literal_load(selected_choices_str, normalize_to_list=True)
            # print("choices_data: ", choices_data)
            
            if choices_data:
                raw_interactions[q_id]["selected_choices"][user_key] = choices_data


            # --- 3. Categories (Map IDs to Chinese names) ---
            # Category IDs are always expected to be lists (even if only one), so we don't normalize single strings
            category_ids = safe_literal_load(cat_str)
            
            # Ensure category_ids is a list (if it was successfully parsed)
            if isinstance(category_ids, list) and category_ids:
                # Map the IDs to their Chinese names
                category_names = [CATEGORY_MAP.get(cat_id, "Unknown") for cat_id in category_ids]
                raw_interactions[q_id]["categories"][user_key] = category_names


            # --- 4. Track flagged status ---
            if is_flagged == 1:
                flagged_question_ids.add(q_id)

        # Step 4: Merge raw interaction data into the final question structure
        final_questions_list = []
        flagged_questions_list = []

        for q_id, q_data in base_questions.items():
            
            # Get the raw interaction data for this specific question
            interaction_data = raw_interactions.get(q_id)
            
            if interaction_data:
                # Replace the placeholder fields with the collected raw data
                q_data["difficulty"] = interaction_data["difficulty"]
                q_data["categories"] = interaction_data["categories"]
                q_data["selected_choices"] = interaction_data["selected_choices"]
            
            final_questions_list.append(q_data)

            # Add to the flagged list if it was flagged by any user
            if q_id in flagged_question_ids:
                flagged_questions_list.append(q_data)

        # Step 5: Write the data to JSON files
        with open(EXTRACTED_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_questions_list, f, ensure_ascii=False, indent=2)
            print(f"Successfully exported {len(final_questions_list)} questions to {EXTRACTED_JSON_PATH} with raw user data.")

        with open(FLAGGED_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(flagged_questions_list, f, ensure_ascii=False, indent=2)
            print(f"Successfully exported {len(flagged_questions_list)} flagged questions to {FLAGGED_JSON_PATH}.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    process_and_export_data()
