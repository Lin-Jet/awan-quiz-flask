import sqlite3
import json
import os
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

def process_and_export_data():
    """
    Connects to the database, aggregates data from user interactions,
    and exports questions to two JSON files.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Step 1: Fetch all base questions and store them in a dictionary
        # This makes it easier to add new fields later
        cursor.execute("SELECT question_id, question, choices, answer, explanation, topic, source FROM questions")
        base_questions = {row[0]: {
            "id": row[0],
            "question": row[1],
            "choices": json.loads(row[2]),
            "answer": row[3],
            "explanation": row[4],
            "topic": row[5],
            "source": row[6],
            "difficulty": 0,  # Placeholder for aggregated value
            "categories": {}   # Placeholder for aggregated value
        } for row in cursor.fetchall()}

        # Dictionaries to hold aggregated data
        difficulty_scores = defaultdict(list)
        question_categories = defaultdict(set)
        flagged_question_ids = set()

        # Step 2: Fetch all user interactions
        cursor.execute("SELECT question_id, selected_difficulty, selected_category, is_flagged FROM user_interactions")
        interactions = cursor.fetchall()

        # Step 3: Aggregate data from interactions
        for interaction in interactions:
            q_id, diff, cat_str, is_flagged = interaction
            
            # Aggregate difficulty scores
            if diff is not None:
                difficulty_scores[q_id].append(diff)
            
            # Aggregate categories
            if cat_str:
                # The category string is a JSON array of string IDs
                category_ids = json.loads(cat_str)
                for cat_id in category_ids:
                    question_categories[q_id].add(cat_id)
            
            # Track flagged questions
            if is_flagged == 1:
                flagged_question_ids.add(q_id)

        # Step 4: Reconstruct the final question data
        final_questions_list = []
        flagged_questions_list = []

        for q_id, q_data in base_questions.items():
            # Calculate average difficulty
            scores = difficulty_scores.get(q_id, [])
            if scores:
                avg_difficulty = round(sum(scores) / len(scores))
                q_data["difficulty"] = avg_difficulty
            
            # Get and sort category IDs
            category_set = question_categories.get(q_id, set())
            sorted_category_ids = sorted(list(category_set), key=int)
            
            # Convert sorted category IDs to a dictionary with names
            category_dict = {cat_id: CATEGORY_MAP.get(cat_id, "Unknown") for cat_id in sorted_category_ids}
            q_data["categories"] = category_dict

            # Add to the main list
            final_questions_list.append(q_data)

            # Add to the flagged list if it was flagged
            if q_id in flagged_question_ids:
                flagged_questions_list.append(q_data)

        # Step 5: Write the data to JSON files
        with open(EXTRACTED_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_questions_list, f, ensure_ascii=False, indent=2)
            print(f"Successfully exported {len(final_questions_list)} questions to {EXTRACTED_JSON_PATH}")

        with open(FLAGGED_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(flagged_questions_list, f, ensure_ascii=False, indent=2)
            print(f"Successfully exported {len(flagged_questions_list)} flagged questions to {FLAGGED_JSON_PATH}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}. Check if 'choices' or 'selected_category' column data is valid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    process_and_export_data()
