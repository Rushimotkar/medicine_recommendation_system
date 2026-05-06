from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    try:
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
        client = MongoClient(mongo_uri)
        
        # Ping the database to check connection
        client.admin.command('ping')
        print("Connected to MongoDB successfully!")
        
        db = client['medico']
        print("Database 'medico' accessed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_database()
