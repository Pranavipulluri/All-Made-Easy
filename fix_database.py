from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check if the column exists
        result = db.session.execute(text("PRAGMA table_info(user)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'profile_pic' not in columns:
            # Add the column if it doesn't exist
            db.session.execute(text("ALTER TABLE user ADD COLUMN profile_pic VARCHAR(200) DEFAULT 'default_profile.jpg'"))
            db.session.commit()
            print("Successfully added profile_pic column to user table")
        else:
            print("profile_pic column already exists")
    except Exception as e:
        print(f"Error: {e}")