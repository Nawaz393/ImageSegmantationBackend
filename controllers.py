from ImagePipeline import Predict, Reconstruct, PreProcessing2d, PreProcessing
from helpers import load_model


def execute_2d_pipeline(image):
    model, device = load_model()
    preprocessor = PreProcessing2d()
    preprocessor.convert_image_to_patches(image)
    predictor = Predict(model, device, image_order_dict={})
    pred_patches = predictor.Predict_2d(
        image_patches=preprocessor.image_patches)
    recon = Reconstruct(image_order_dict={},
                        orignal_affine=None, orignal_header=None)
    recon_image = recon.construct_2d_image_and_return_image(
        image_patches=pred_patches)
    return recon_image


def execute_3d_pipeline(image_temp_path):
    model, device = load_model()
    print("Model loaded")
    print("Preprocessor initialized")
    preprocessor = PreProcessing()
    print(preprocessor.image_patches_dict)
    preprocessor.convert_image_to_patches(image_path=image_temp_path)
    print("Image patches extracted")
    print("predictor initialized")
    predictor = Predict(
        model, device, image_order_dict=preprocessor.image_patches_dict)
    predictor.predict()
    print("Prediction complete")
    print("Reconstructor initialized")
    recon = Reconstruct(image_order_dict=predictor.perd_masks_order_dict,
                        orignal_affine=preprocessor.orignal_affine, orignal_header=preprocessor.orignal_header)
    reconstructed_volume = recon.construct_3d_image()
    print("Reconstruction complete")
    return reconstructed_volume
