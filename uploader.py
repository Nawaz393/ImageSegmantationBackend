from cloudinary.uploader import upload, upload_large


def upload_2d_images_to_cloudinary(image, mask):
    try:
        print("Uploading 2D images to Cloudinary...")
        upload_result1 = upload(image, folder="2d_images")

        print(upload_result1["secure_url"])

        upload_result2 = upload(mask, folder="2d_masks")
        print(upload_result2["secure_url"])
        return (upload_result1["secure_url"], upload_result2["secure_url"])
    except Exception as e:
        print(e)
        return None


def upload_3d_file_to_cloudinary(file):
    try:
        print("uploading 3d image to cloudinary")
        upload_res = upload_large(
            file, folder="3d_image", chunk_size=6000000, resource_type="raw")
        print(upload_res["secure_url"])
        return upload_res["secure_url"]
    except Exception as e:
        print(e)
        return None
