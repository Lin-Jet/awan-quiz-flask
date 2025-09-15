import sqlite3
import json
import os

# --- File Path Configuration ---
# Change this to the path of your SQLite database file.
DATABASE_PATH = 'app.db' 
# This is the path for the output JSON file. You can change this.
OUTPUT_JSON_PATH = 'questions_export.json'

def export_questions_to_json(db_path, json_path):
    """
    Exports all questions from a SQLite database to a JSON file.
    """
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute query to fetch all question data
        # **UPDATE: Added 'subject' column to the SELECT statement**
        cursor.execute("SELECT id, question, choices, answer, explanation, topic, difficulty, source, category FROM questions")
        rows = cursor.fetchall()
        
        # Prepare the JSON array
        questions_array = []
        
        # Iterate through each row and convert to dictionary format
        for row in rows:
            # Map database column values to JSON keys
            question_dict = {
                "id": row[0],
                "question": row[1],
                "choices": json.loads(row[2]),  # Parse the JSON string in the choices column
                "answer": row[3],
                "explanation": row[4],
                "topic": row[5],
                "difficulty": row[6],
                "source": row[7],
                "category": row[8],
            }
            questions_array.append(question_dict)

        # Write the Python array to the JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            # Use ensure_ascii=False to correctly store Chinese characters
            # indent=2 to make the output file more readable
            json.dump(questions_array, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully exported {len(questions_array)} questions to {json_path}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

# Run the script
if __name__ == "__main__":
    export_questions_to_json(DATABASE_PATH, OUTPUT_JSON_PATH)
