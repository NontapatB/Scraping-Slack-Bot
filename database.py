from pymongo import MongoClient

# Function to connect to the MongoDB database
def connect_to_database(mongo_uri, db_name):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db

# Functions to access different collections in the database
def profile_uris_collection(db):
    return db['profile_uris']

def categories_collection(db):
    return db['categories']

def bookmarks_collection(db):
    return db['bookmarks']

def populars_collection(db):
    return db['populars']

def facebook_mapping_categories_collection(db):
    return db['facebook_mapping_categories']

def website_categories_collection(db):
    return db['website_categories']

# Function to validate data before inserting URL into the database
def validate_data_before_insert_url(url, title, link, channel_id):
    # Check if all required fields are present
    if url and title and link and channel_id:
        return True
    else:
        return False

# Function to validate data before inserting bookmark into the database
def validate_data_before_insert_bookmark(url, title, user_id, status):
    # Check if all required fields are present
    if url and title and user_id and status:
        return True
    else:
        return False
    


        

