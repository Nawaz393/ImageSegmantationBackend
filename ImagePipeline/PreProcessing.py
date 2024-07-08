import os
import cv2 as cv
import numpy as np
import nibabel as nib
import time


class PreProcessing:
    def __init__(self):
        self.image_order_dict = {}
        # self.output_image_dir=output_image_dir
        self.image_patches_dict = {}
        self.orignal_affine = None
        self.orignal_header = None

        # if not os.path.exists(output_image_dir):
        #     os.makedirs(output_image_dir)

    def normalize_volume(self, volume):
        """
        Normalize the volume to the range [0, 255].
        Args:
        - volume: Input 3D volume.
        Returns:
        - normalized_volume: Normalized 3D volume.
        """

        volume = ((volume - volume.min()) /
                  (volume.max() - volume.min())*255).astype(np.uint8)
        # else:
        #     volume[volume>0]=255
        return volume

    def convert_from_3d_to_2d(self, image, is_label):
        # Set the threshold value
        processed_images = []
        image = self.normalize_volume(image)
        for z in range(image.shape[2]):
            slice_data = image[:, :, z]
            if not is_label:
                slice_data = np.where(slice_data > 63, slice_data, 0)
                slice_data = cv.GaussianBlur(slice_data, (3, 3), 0)
            processed_images.append(slice_data)
        return processed_images

    def extract_patches(self, image, patch_size, stride):
        """
        Extract patches from a 2D image.
        Parameters:
        - image: 2D numpy array representing the image.
        - patch_size: Tuple (patch_height, patch_width) specifying the size of each patch.
        - stride: Tuple (vertical_stride, horizontal_stride) specifying the stride for patch extraction.
        Returns:
        - patches: List of extracted patches.
        """
        patches = []
        height, width = image.shape
        # Iterate through the image with the specified stride and extract patches
        for i in range(0, height - patch_size[0] + 1, stride[0]):
            for j in range(0, width - patch_size[1] + 1, stride[1]):
                patch = image[i:i + patch_size[0], j:j + patch_size[1]]
                patches.append(patch)
        return patches

    def convert_image_to_patches(self, image_path, patch_size=(128, 128), stride=(128, 128)):
        image = nib.load(image_path)
        image_data = image.get_fdata()
        print(image_data.shape)
    
        self.orignal_affine = image.affine
        self.orignal_header = image.header
        image_slices = self.convert_from_3d_to_2d(image_data, False)
        print(image_slices[0])
      
        for idx, image_slice in enumerate(image_slices):
            # self.image_order_dict[idx] = []
            self.image_patches_dict[idx] = []
            image_patches = self.extract_patches(
                image_slice, patch_size, stride)
            for jdx, image_patch in enumerate(image_patches):
                self.image_patches_dict[idx].append(image_patch)
        print(self.image_order_dict)
