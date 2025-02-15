from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from services.mongo_services import users_collection
from services.s3_services import upload_to_s3
from extract import extract_text_from_form, store_data_in_mongo  # Import functions

app = Flask(__name__, template_folder="templates")

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDFs and images are allowed"}), 400

    filename = secure_filename(file.filename)
    file_extension = filename.rsplit(".", 1)[1].lower()

    if file_extension == "pdf":
        file_url = upload_to_s3(file, filename)
        users_collection.insert_one({"url": file_url})
        return jsonify({"message": "PDF uploaded successfully", "url": file_url})
    
    elif file_extension in {"jpg", "jpeg", "png"}:
        image_bytes = file.read()  # Read image as bytes
        extracted_data = extract_text_from_form(image_bytes)  # Process with extract.py
        store_data_in_mongo(extracted_data)  # Store extracted data in MongoDB
        return jsonify({"message": "Image processed successfully", "data": extracted_data})

if __name__ == "__main__":
    app.run(debug=True)
