from flask import Flask, render_template, request
import json
import boto3
import os
from pymongo import MongoClient

app = Flask(__name__)

# AWS Textract client
textract = boto3.client(
    'textract',
    aws_access_key_id="access",
    aws_secret_access_key="secret",
    region_name="ap-south-1"
)

# AWS S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id="access",
    aws_secret_access_key="secret",
    region_name="ap-south-1"
)
S3_BUCKET = "nitrogen1"

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["database"]
collection = db["data"]

def extract_text_from_form(image_bytes):
    response = textract.analyze_document(
        Document={'Bytes': image_bytes},
        FeatureTypes=["FORMS"]
    )

    key_map = {}
    value_map = {}
    block_map = {}

    for block in response["Blocks"]:
        block_map[block["Id"]] = block
        if block["BlockType"] == "KEY_VALUE_SET":
            if "KEY" in block["EntityTypes"]:
                key_map[block["Id"]] = block
            else:
                value_map[block["Id"]] = block

    extracted_data = {}
    for key_id, key_block in key_map.items():
        key_text = extract_text(key_block, block_map)
        value_block = find_value_block(key_block, value_map)
        value_text = extract_text(value_block, block_map) if value_block else None

        if key_text and value_text:
            extracted_data[key_text] = value_text

    return extracted_data

def extract_text(block, block_map):
    text = ""
    if "Relationships" in block:
        for rel in block["Relationships"]:
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    word_block = block_map.get(child_id)
                    if word_block and "Text" in word_block:
                        text += word_block["Text"] + " "
    return text.strip()

def find_value_block(key_block, value_map):
    if "Relationships" in key_block:
        for rel in key_block["Relationships"]:
            if rel["Type"] == "VALUE":
                for value_id in rel["Ids"]:
                    return value_map.get(value_id)
    return None

def store_data_in_mongo(data):
    if data:
        collection.insert_one(data)

def store_in_s3(file, file_name):
    s3.upload_fileobj(file, S3_BUCKET, file_name)

@app.route('/')
def upload_form():
    return '''
    <h2>Upload PDFs or Images</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="files" multiple required>
        <input type="submit" value="Upload">
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return "No files uploaded."
    files = request.files.getlist('files')
    if not files:
        return "No files selected."
    
    for file in files:
        if file.filename == '':
            continue
        file_bytes = file.read()
        extracted_data = extract_text_from_form(file_bytes)
        store_data_in_mongo(extracted_data)
        file.seek(0)  # Reset file pointer before uploading to S3
        store_in_s3(file, file.filename)
    
    return "Files processed, data stored in MongoDB, and files uploaded to S3."

if __name__ == '__main__':
    app.run(debug=True)
