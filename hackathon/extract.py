
import json
from pymongo import MongoClient

# AWS Textract client
import boto3

textract = boto3.client(
    'textract',
    aws_access_key_id="access_key",
    aws_secret_access_key="secret_key",
    region_name="ap-south-1"      # Change based on your AWS region
)


# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")  # Change if using cloud MongoDB
db = mongo_client["database"]
collection = db["data"]

def extract_text_from_form(image_bytes):
    """
    Extract key-value pairs from a financial form using Amazon Textract.
    :param image_bytes: Binary content of the image/PDF
    :return: Dictionary of extracted key-value pairs
    """
    response = textract.analyze_document(
        Document={'Bytes': image_bytes},
        FeatureTypes=["FORMS"]
    )

    key_map = {}
    value_map = {}
    block_map = {}

    # Parse response
    for block in response["Blocks"]:
        block_map[block["Id"]] = block
        if block["BlockType"] == "KEY_VALUE_SET":
            if "KEY" in block["EntityTypes"]:
                key_map[block["Id"]] = block
            else:
                value_map[block["Id"]] = block

    # Extract key-value pairs
    extracted_data = {}
    for key_id, key_block in key_map.items():
        key_text = extract_text(key_block, block_map)
        value_block = find_value_block(key_block, value_map)
        value_text = extract_text(value_block, block_map) if value_block else None

        if key_text and value_text:
            extracted_data[key_text] = value_text

    return extracted_data

def extract_text(block, block_map):
    """
    Extract text from a block.
    """
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
    """
    Find the corresponding value block for a given key block.
    """
    if "Relationships" in key_block:
        for rel in key_block["Relationships"]:
            if rel["Type"] == "VALUE":
                for value_id in rel["Ids"]:
                    return value_map.get(value_id)
    return None

def store_data_in_mongo(data):
    """
    Store extracted data in MongoDB.
    """
    if data:
        collection.insert_one(data)
        print("Data stored successfully in MongoDB.")
    else:
        print("No data to store.")

# Example usage
if __name__ == "__main__":
    file_path = r"C:\Users\roman\Downloads\pay.pdf"  # Use raw string (r"")

    with open(file_path, "rb") as file:
        image_bytes = file.read()

    extracted_data = extract_text_from_form(image_bytes)
    print("Extracted Data:", json.dumps(extracted_data, indent=2))

    store_data_in_mongo(extracted_data)
