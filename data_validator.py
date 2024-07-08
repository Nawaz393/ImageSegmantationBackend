import os


def validate_image_data(data):
    if not ('imageName' in data or 'name' in data or 'description' in data):
        return {"status": False, "message": "Invalid data format"}
    if len(data["name"]) < 3:
        return {"status": False, "message": "name must be atleast 3 characters long"}
    if len(data["description"]) < 15:
        return {"status": False, "message": "description must be atleast 15 characters long"}
    if not is_image_exists(data["imageName"]):
        return {"status": False, "message": "Image does not exists please upload the image"}
    return {"status": True, "message": "Data is valid"}


def validate_volume_data(data):
    if not ('imageName' in data or 'name' in data or 'description' in data):
        return {"status": False, "message": "Invalid data format"}
    if len(data["name"]) < 3:
        return {"status": False, "message": "name must be atleast 3 characters long"}
    if len(data["description"]) < 15:
        return {"status": False, "message": "description must be atleast 15 characters long"}
    if not is_volume_exists(data["imageName"]):
        return {"status": False, "message": "Image does not exists please upload the image"}
    return {"status": True, "message": "Data is valid"}


def is_volume_exists(imageName):
    if os.path.exists(os.path.join("uploads", imageName)):
        return True
    return False


def is_image_exists(imageName):
    if os.path.exists(os.path.join("static", imageName)):
        return True
    return False
