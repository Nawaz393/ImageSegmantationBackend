import numpy as np
import os
import nibabel as nib
from PIL import Image


class Reconstruct:
    def __init__(self, image_order_dict, orignal_affine, orignal_header):
    
        self.image_order_dict = image_order_dict
        self.orignal_affine = orignal_affine
        self.orignal_header = orignal_header

    def reconstruct_image(self, patches, original_shape=(512, 512), patch_size=(128, 128), stride=(128, 128)):
        """
        Reconstruct the image from the extracted patches.
        Parameters:
        - patches: List of extracted patches.
        - original_shape: Tuple (original_height, original_width) specifying the size of the original image.
        - patch_size: Tuple (patch_height, patch_width) specifying the size of each patch.
        - stride: Tuple (vertical_stride, horizontal_stride) specifying the stride for patch extraction.
        Returns:
        - reconstructed_image: 2D numpy array representing the reconstructed image.
        """
        height, width = original_shape
        reconstructed_image = np.zeros((height, width), dtype=patches[0].dtype)
        patch_index = 0
        for i in range(0, height - patch_size[0] + 1, stride[0]):
            for j in range(0, width - patch_size[1] + 1, stride[1]):
                reconstructed_image[i:i + patch_size[0],
                                    j:j + patch_size[1]] = patches[patch_index]
                patch_index += 1
        return reconstructed_image

    def construct_3d_image(self):
        image_slices = []
        for idx, image_patches_key in enumerate(self.image_order_dict.keys()):
            image_patches = self.image_order_dict[image_patches_key]

            print(np.array(image_patches).shape)
            print(image_patches[0])
            recon_2d_image = self.reconstruct_image(image_patches)
            image_slices.append(recon_2d_image)
        volume_arr = np.stack(image_slices, axis=-1)
        volume_img = nib.Nifti1Image(
            volume_arr, affine=self.orignal_affine, header=self.orignal_header)
        return volume_img
        # nib.save(volume_img, os.path.join(f"{self.path}.nii.gz"))

    def construct_2d_image_and_return_image(self, image_patches):
        try:
            print(len(image_patches))
            recon_2d_image = self.reconstruct_image(image_patches)
            scaled_image = (recon_2d_image * 255).astype(np.uint8)
            pil_image = Image.fromarray(scaled_image)
            return pil_image
        except Exception as e:
            print("Error:", e)
            return None
