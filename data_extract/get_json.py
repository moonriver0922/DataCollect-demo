from pymongo import MongoClient
import json
import os

def export_collection_to_file(database_name, collection_name, output_file_path):
    client = MongoClient('localhost', 27017)
    db = client[database_name]
    collection = db[collection_name]

    with open(output_file_path, 'w') as output_file:
        for document in collection.find():
            json.dump(document, output_file)
            output_file.write('\n')


output_dir_path = "./data"
database_name = "LocGPT"
collections = ["collection1", "collection2", "collection3"]

if not os.path.exists(output_dir_path):
    os.makedirs(output_dir_path)
for collection_name in collections:
    output_file_path = f"{output_dir_path}/{collection_name}.json"
    export_collection_to_file(database_name, collection_name, output_file_path)
