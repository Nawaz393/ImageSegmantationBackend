import numpy as np
from torchvision import transforms
import torch
import os
class Predict:
    def __init__(self, model, device,image_order_dict):
        self.model = model
        self.device = device
        self.image_order_dict=image_order_dict
        self.perd_masks_order_dict={}
        self.model.eval()

        

    def single_image_inference(self, image, model, device):
            
            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((128, 128)),
                transforms.ToTensor()
            ])
    
            img = transform(image).float().to(device)
            img = img.unsqueeze(0)
    
            with torch.no_grad():
                pred_mask = model(img)
            pred_mask = pred_mask.squeeze(0).cpu().permute(1, 2, 0).squeeze(-1)
            pred_mask[pred_mask < 0] = 0
            pred_mask[pred_mask > 0] = 1
    
            return pred_mask.numpy()

    def predict(self):
        print("Predicting")
        for image_patches_key in self.image_order_dict.keys():
            pred_patches = []
            for image_patch in self.image_order_dict[image_patches_key]:
                pred_mask = self.single_image_inference(np.array(image_patch), self.model, self.device)
                pred_patches.append(pred_mask)
            self.perd_masks_order_dict[image_patches_key]=pred_patches
        print("Prediction complete")

    
    def Predict_2d(self, image_patches):
        print("Predicting")
        pred_patches = []
        for image_patch in image_patches:
            pred_mask = self.single_image_inference(np.array(image_patch), self.model, self.device)
            pred_patches.append(pred_mask)
        print("Prediction complete")
        return pred_patches
