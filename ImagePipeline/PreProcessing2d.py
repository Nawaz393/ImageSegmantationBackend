import os
import cv2 as cv
import numpy as np
import nibabel as nib
from PIL import Image



class PreProcessing2d:
    def __init__(self):
        self.image_patches=[]


    def extract_patches(self, image, patch_size=(128,128), stride=(128,128)):
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
        image=np.array(Image.open(image_path).convert('L'))
        image=np.where(image>63,image,0)
        image=cv.GaussianBlur(image,(3,3),0)
        self.image_patches=self.extract_patches(image, patch_size, stride)
              
        

