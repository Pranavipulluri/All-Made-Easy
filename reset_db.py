from app import app, db

print("Warning: This will delete all data in the database and recreate the tables.")
confirmation = input("Do you want to continue? (yes/no): ")

if confirmation.lower() == 'yes':
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database has been reset successfully!")
else:
    print("Operation cancelled.")