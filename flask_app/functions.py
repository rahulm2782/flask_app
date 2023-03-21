# importing the necessary libraries.
from PIL import Image
import numpy as np
import io
import torch
from transformers import Swin2SRForImageSuperResolution
from transformers import Swin2SRImageProcessor
import keras
import base64


# loading the models.
model_mirnet = keras.models.load_model('./models/keras_mirnet.h5')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_swin = Swin2SRForImageSuperResolution.from_pretrained("caidas/swin2SR-classical-sr-x2-64").to(device)

model_swin.load_state_dict(torch.load("./models/swin2sr_model.pth"))


def enhance_image(img):
    """
    It takes an image as input, resizes it to 480x480 if it's larger than that, and then runs it through
    the model
    
    :param img: The image that you want to enhance
    :return: The enhanced image is being returned.
    """
    image = Image.open(io.BytesIO(img))
    width,height = image.size
    if width < 480 and height < 480:
        pass
    else:
        image = image.resize((480,480))

    image = np.array(image)
    image = image/255.0
    image = np.expand_dims(image,axis=0)

    output = model_mirnet.predict(image)


    enhanced_image = output[0]
    enhanced_image = np.clip(enhanced_image*255,0,255)
    enhanced_image = enhanced_image.astype(np.uint8)
    enhanced_image = Image.fromarray(enhanced_image)
    return enhanced_image

def buffer(path):
    """
    It takes a path to an image and returns a base64 encoded string of the image.
    
    :param path: The path to the image file
    :return: A string of base64 encoded data.
    """
    image = Image.open(path)
    temp = io.BytesIO()
    image.save(temp, format='PNG')
    return base64.b64encode(temp.getvalue()).decode()


def img_enhance(path):
    """
    It takes an image, resizes it to 500x500, converts it to a tensor, runs it through the model, and
    returns the output.
    
    :param path: The path to the image file
    :return: The image size and the enhanced image.
    """
    image = Image.open(io.BytesIO(path))

    # get the size of the image
    width, height = image.size

    # It's resizing the image to 500x500 if it's larger than that.
    if width < 500 and height < 500:
        pass
    else:
        image = image.resize((500,500))
    image_size = image.size
    # Converting the image to a tensor.
    processor = Swin2SRImageProcessor()  #default rescaled
    pixel_values = processor(image, return_tensors="pt").pixel_values.to(device)
    
    # It's trying to run the model on the GPU, and if it fails, it will run it on the CPU.
    try:
        with torch.no_grad():
            outputs = model_swin(pixel_values)
    except RuntimeError as error:
        if 'out of memory' in str(error):
            print('Warning: out of GPU memory. Switching to CPU.')
            torch.cuda.empty_cache()
            model_swin_cpu = model_swin.to('cpu')
            pixel_values_cpu = pixel_values.to('cpu')
           # It's telling the model not to calculate the gradients.
            with torch.no_grad():
                outputs = model_swin_cpu(pixel_values_cpu)
        else:
            raise error
    else:
        # It's taking the output of the model, and it's converting it to a numpy array.
        output = outputs.reconstruction.data.squeeze().float().cpu().clamp_(0, 1).numpy()
        # It's moving the axis from 0 to -1.
        output = np.moveaxis(output, source=0, destination=-1)
        # It's converting the output to a numpy array, and then it's multiplying it by 255.0, rounding
        # it, and then it's converting it to an unsigned integer.
        output = (output * 255.0).round().astype(np.uint8)  
        output = Image.fromarray(output)
        
        return image_size,output
