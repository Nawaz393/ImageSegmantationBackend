from flask import Flask, jsonify, send_from_directory, current_app
from flask import request
from controllers import execute_2d_pipeline, execute_3d_pipeline
from dal import insert_image_data_to_db
from pymongo import MongoClient
import cloudinary
from flask_cors import CORS
import nibabel as nib
from werkzeug.utils import secure_filename
import tempfile
import time
import jwt
from bson import ObjectId

import os

from data_validator import validate_image_data, validate_volume_data

app = Flask(__name__)

CORS(app)
MONGO_URI = "mongodb+srv://root:12345678.@cluster0.eldclyy.mongodb.net/SegmantationDb?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database()


cloudinary.config(
    cloud_name="dcqprkiml",
    api_key="749559781292592",
    api_secret="hLpRPyEqGjmsPabD4YR2NcgSzYc"
)


ALLOWED_EXTENSIONS = {'nii', 'nii.gz'}


def allowed_file(filename):
    filename_spilt = filename.split(".")
    if (len(filename_spilt) < 2):
        return False
    elif len(filename_spilt) == 3:
        return '.'.join(filename_spilt[1:3]) in ALLOWED_EXTENSIONS
    elif len(filename_spilt) == 2:
        return filename_spilt[-1] in ALLOWED_EXTENSIONS
    # return '.' in filename and \
    #        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def hello_world():
    # Get the JWT token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Missing token"}), 400

    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    try:
        # Decode the token
        decoded_token = jwt.decode(token, "mnk393", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    # Print the decoded token
    print("Decoded token:", str(decoded_token["userId"]))
    # Find all documents in the 'Image' collection
    image_data = db.Image.find()
    # Convert cursor to a list of dictionaries
    image_list = list(image_data)
    print(image_list)
    # Convert the list to JSON format
    # json_data = jsonify(image_list)

    return jsonify(image_list)


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


@app.route("/u")
def hello_world2():
    res = db.Image.insert_one(
        {"userId": "1", "imagePath": "path", "maskPath": "mask", "imageType": "type"})
    return jsonify({"message": "Data inserted successfully", "id": str(res.inserted_id)})


@app.route("/segment2d", methods=['POST'])
def segment2d():
    # Check if file is present in the request
    is_token, result = get_user_id_from_jwt(request)
    if not is_token:
        return jsonify(result)

    if 'file' not in request.files:
        return jsonify({"error": "No file found in the request"}), 400
    file = request.files['file']
    # Check if the file name is empty
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Check if the file is an allowed format (you can define your allowed formats)
    allowed_extensions = {'jpg', 'jpeg', 'png'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({"error": "Unsupported file format"}), 400
    # Generate a secure file name and save the file to a temporary location
    file_name = str(int(time.time())) + '_' + secure_filename(file.filename)
    file_path = os.path.join("static", file_name)
    file.save(file_path)
    # Execute 2D segmentation pipeline
    try:
        segmented_image = execute_2d_pipeline(file_path)
    except Exception as e:
        # If an error occurs during processing, remove the temporary file and return an error response
        os.remove(file_path)
        return jsonify({"error": f"Error in processing image: {str(e)}"}), 500
    # Check if segmentation was successful
    if segmented_image is not None:
        # Save the segmented image
        segmented_file_name = str(int(time.time())) + \
            '_segmented_' + secure_filename(file.filename)
        segmented_path = os.path.join("static", segmented_file_name)
        segmented_image.save(segmented_path)
        res = insert_image_data_to_db(
            db, result["userId"], file_name, segmented_file_name, "2d")
        if res is True:
            return jsonify({"file_path": file_path, "segmented_file_path": segmented_file_name}), 200
        return jsonify({"error": "internal server error"}), 500
    else:
        # If segmentation was unsuccessful, remove the temporary file and return an error response
        os.remove(file_path)
        return jsonify({"error": "Error in processing image: segmentation failed"}), 500


@app.route("/segment3d", methods=['POST'])
def segment3d():
    try:
        # Check if file is present in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file found"}), 400

        volume = request.files['file']

        # Check if the file has a valid filename
        if not volume.filename:
            return jsonify({"error": "No file selected"}), 400

        # Check file format
        file_name = volume.filename
        if not (file_name.endswith(".nii.gz") or file_name.endswith(".nii")):
            return jsonify({"error": "Invalid file format"}), 400

        # Save the file temporarily to disk
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension(file_name)) as tmp_file:
            tmp_file.write(volume.read())
            tmp_file.flush()
            print("Temporary file path:", tmp_file.name)

            # Execute 3D segmentation pipeline
            segmented_volume = execute_3d_pipeline(tmp_file.name)

            # Save both original and segmented volumes
        paths = save_original_and_segmented_volumes(
            tmp_file.name, segmented_volume, file_name)
        if paths is None:
            return jsonify({"error": "An error occurred: segmentation failed"}), 500
        file_path, segmented_file_path = paths
        res = insert_image_data_to_db(
            db, "1", file_path, segmented_file_path, "3d")
        if res is True:
            return jsonify({"file_path": file_path, "segmented_file_path": segmented_file_path}), 200
        return jsonify({"error": "internal server error"}), 500

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


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


def save_original_and_segmented_volumes(original_file_path, segmented_volume, file_name):
    try:
        # Save original volume
        original_volume = nib.load(original_file_path)
        original_volume_name = str(int(time.time()))+"_"+file_name
        original_volume.to_filename(os.path.join(
            "uploads", original_volume_name))

        # Save segmented volume
        segmented_file_name = f"segmented_{int(time.time())}_{file_name}"
        segmented_volume_path = os.path.join("uploads", segmented_file_name)
        nib.save(segmented_volume, segmented_volume_path)
        return original_volume_name, segmented_file_name
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    finally:
        # Clean up temporary file
        os.remove(original_file_path)


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


@app.route("/getVolume", methods=['GET'])
def send_vol():
    return send_from_directory('uploads', 'label_010.nii', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
