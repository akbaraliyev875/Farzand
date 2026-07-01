import sqlite3

def fix_db():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0;")
        conn.commit()
        print("Column 'points' added to users.")
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    fix_db()
