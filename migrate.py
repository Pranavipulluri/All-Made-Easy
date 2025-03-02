from app import app, db  # Import your app and db instances

if __name__ == "__main__":
    with app.app_context():
        # Add the missing column
        db.engine.execute('ALTER TABLE user ADD COLUMN profile_pic VARCHAR(200) DEFAULT "default_profile.jpg"')
        print("Column added successfully!")