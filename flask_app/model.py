#importing necessary libraries
from flask import Flask,render_template,jsonify,request
import functions
import io
import base64


#creating a flask app
app = Flask(__name__)

@app.route('/')
def index():
    return "Model Index"


#Dark image enhancer
@app.route('/enhance',methods=['POST'])
def enhance():
    """
    It takes an image file, enhances it using the function defined, saves it to a buffer, encodes it, and returns it as a JSON
    object.
    :return: The enhanced image is being returned as a base64 encoded string.
    """
    image_file = request.files['file'].read()  #reading file as binary
    enhanced_image = functions.enhance_image(image_file)  
    buffer = io.BytesIO()
    enhanced_image.save(buffer,format='JPEG')
    encoded_output_img = base64.b64encode(buffer.getvalue()).decode() #converting the image into byte strings

    return jsonify({"OutputImage" : encoded_output_img})


#Low resolution image enhancer
@app.route('/superimage', methods=['POST'])
def super_image():
    """
    It takes an image, enhances it, and returns the enhanced image and the size of the original and
    enhanced images.
    :return: The super_image is being returned as a base64 encoded string.
    """
    image = request.files['image'].read()

    original_image_size,super_image = functions.img_enhance(image)  #refer image_enhance in functions.py
    super_image_size = super_image.size

    buffer = io.BytesIO()
    super_image.save(buffer,format='JPEG')
    encoded_super_image = base64.b64encode(buffer.getvalue()).decode()
    return jsonify({'super_image':encoded_super_image,
                    'enhanced_size':super_image_size,
                    'original_size':original_image_size})

if __name__ == '__main__':
    app.run(debug=True,port=8080)

