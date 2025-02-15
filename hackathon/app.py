from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from services.mongo_services import users_collection
from services.s3_services import upload_to_s3

app = Flask(__name__, template_folder="templates")

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

    allowed_extensions = {"pdf", "jpeg", "jpg"}
    if file and file.filename.split(".")[-1].lower() in allowed_extensions:
        filename = secure_filename(file.filename)
        file_url = upload_to_s3(file, filename)

        users_collection.insert_one({"url": file_url})
        return jsonify({"message": "File uploaded successfully", "url": file_url})

    return jsonify({"error": "Invalid file type. Only PDFs and JPEGs are allowed"}), 400

if __name__ == "__main__":
    app.run(debug=True)
