from flask import Flask, jsonify, send_from_directory, current_app
from flask import request
from controllers import execute_2d_pipeline, execute_3d_pipeline
from dal import insert_image_data_to_db
from pymongo import MongoClient
from flask_cors import CORS
import nibabel as nib
from werkzeug.utils import secure_filename
import time
import jwt


import os

from data_validator import validate_image_data, validate_volume_data

app = Flask(__name__)

CORS(app)
MONGO_URI = "mongodb+srv://root:12345678.@cluster0.eldclyy.mongodb.net/SegmantationDb?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database()


def get_user_id_from_jwt(request):
    token = request.headers.get('Authorization')
    if not token:
        return False, {"error": "Missing token"}
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]
    try:
        # Decode the token
        decoded_token = jwt.decode(token, "mnk393", algorithms=["HS256"])
        return True, decoded_token
    except jwt.ExpiredSignatureError:
        return False, {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return False, {"error": "Invalid token"}


@app.route("/download-volume/<path:path>", methods=['GET', 'POST'])
def get_file(path):
    try:
        print(path)
        return send_from_directory('uploads', path, as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        return jsonify({"message": "File not found"}), 404


@app.route("/download-image/<path:path>", methods=['GET', 'POST'])
def download_image(path):
    try:
        return send_from_directory('static', path, as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        return jsonify({"message": "File not found"}), 404


@app.route("/image/<path:path>", methods=['GET', 'POST'])
def get_image(path):
    try:
        print(path)
        return current_app.send_static_file(path)
    except FileNotFoundError as e:
        print(e)
        return jsonify({"message": "File not found"}), 404


def file_extension(filename):
    return ".nii.gz" if filename.endswith(".nii.gz") else ".nii"


@app.route('/uploadvolume', methods=['POST'])
def upload_volume():
    if 'file' not in request.files:
        return jsonify({"error": "No file found"}), 400
    volume = request.files['file']
    if not volume.filename:
        return jsonify({"error": "No file selected"}), 400
    file_name = f"{int(time.time())}_{secure_filename(volume.filename)}"
    if not (file_name.endswith(".nii.gz") or file_name.endswith(".nii")):
        return jsonify({"error": "Invalid file format"}), 400
    # Create upload folder if it doesn't exist
    os.makedirs("uploads", exist_ok=True)  # Safe folder creation
    # Define full upload path
    upload_path = os.path.join("uploads", file_name)
    try:
        # Save file to upload folder
        volume.save(upload_path)

        # Return success response with file path
        return jsonify({"message": "File uploaded successfully", "fileName": file_name}), 200

    except Exception as e:
        # Handle upload errors gracefully
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/uploadimage', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file found"}), 400
    image = request.files['file']
    if not image.filename:
        return jsonify({"error": "No file selected"}), 400
    file_name = f"{int(time.time())}_{secure_filename(image.filename)}"
    if not (file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png")):
        return jsonify({"error": "Invalid file format"}), 400
    # Create upload folder if it doesn't exist
    os.makedirs("static", exist_ok=True)  # Safe folder creation
    # Define full upload path
    upload_path = os.path.join("static", file_name)
    try:
        # Save file to upload folder
        image.save(upload_path)

        # Return success response with file path
        return jsonify({"message": "File uploaded successfully", "fileName": file_name}), 200

    except Exception as e:
        # Handle upload errors gracefully
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/segment2d1', methods=['POST'])
def segment2d1():
    is_token, result = get_user_id_from_jwt(request)
    if not is_token:
        return jsonify(result)

    data = request.get_json()
    print(data)
    validate_data = validate_image_data(data)
    if not validate_data["status"]:
        return jsonify({"error": validate_data["message"]}), 400
    image_name = data["imageName"]
    image_path = os.path.join("static", image_name)
    name = data["name"]
    description = data["description"]
    # Execute 2D segmentation pipeline
    segmented_image = execute_2d_pipeline(image_path)
    if segmented_image is not None:
        segmented_file_name = f"segmented_{int(time.time())}_{image_name}"
        segmented_path = os.path.join("static", segmented_file_name)
        segmented_image.save(segmented_path)
        res = insert_image_data_to_db(
            db, result["userId"], image_name, segmented_file_name, "2d", name, description)
        if res is not None:
            return jsonify({'id': res}), 200
        return jsonify({"error": "internal server error"}), 500
    else:
        return jsonify({"error": "Error in processing image: segmentation failed"}), 500


@app.route("/segment3d1", methods=['POST'])
def segement3d1():
    is_token, result = get_user_id_from_jwt(request)
    if not is_token:
        return jsonify(result)
    data = request.get_json()
    print(data)
    validate_data = validate_volume_data(data)
    if not validate_data["status"]:
        return jsonify({"error": validate_data["message"]}), 400
    image_name = data["imageName"]
    image_path = os.path.join("uploads", image_name)
    name = data["name"]
    description = data["description"]
    # Execute 3D segmentation pipeline
    segmented_volume = execute_3d_pipeline(image_path)
    if segmented_volume is not None:
        segmented_volume_name = f"segmented_{int(time.time())}_{image_name}"
        nib.save(segmented_volume, os.path.join(
            "uploads", segmented_volume_name))
        res = insert_image_data_to_db(
            db, result["userId"], image_name, segmented_volume_name, "3d", name, description
        )
        if res is not None:
            return jsonify({'id': res}), 200
        return jsonify({"error": "internal server error"}), 500
    else:
        return jsonify({"error": "Error in processing image: segmentation failed"}), 500


if __name__ == "__main__":
    app.run(debug=True)
