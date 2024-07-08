import torch
from PIL import Image
import io

def load_model():
    model = torch.jit.load(
        r"G:\python\models\Single_SpineSegmentationv8.2_cpu.pth")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return model, device

def convert_image_to_compatible_format(image):
    image = Image.open(image)
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        image_data = output.getvalue()
        return image_data
    