from bson import ObjectId


def insert_image_data_to_db(db, user_id, image_path, mask_path, image_type, name, description):
    """
    Insert image data to the database.
    """
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    try:
        res = db["images"].insert_one({
            "user_id": user_id,
            "image_path": image_path,
            "mask_path": mask_path,
            "image_type": image_type,
            "name": name,
            "description": description
        })
        print(res)
        if res:
            return str(res.inserted_id)
    except Exception as e:
        print(e)
        return None
