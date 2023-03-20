from flask import Flask,render_template,request
import base64
import requests
from PIL import Image
import io
import functions
import os

#home page
app = Flask(__name__)
@app.route('/')
def index():
    """
    It takes the images from the images folder and encodes them into base64 strings
    :return: the rendered template of index.html which is the home page.
    """
    dark_image_encode = functions.encode(functions.buffer('./images/ying-modified.png'))
    both_image_encode = functions.encode(functions.buffer('./images/both.png'))
    return render_template('index1.html',dark_image_encode=dark_image_encode,
                           both_image_encode=both_image_encode)
@app.route('/about')
def about():
    dark_en_encoded = functions.encode(functions.buffer('./images/dark.png'))
    en_encode = functions.encode(functions.buffer('./images/en.png'))
    dr_en_encode = functions.encode(functions.buffer('./images/dk_en.png'))
    return render_template('about.html',dark_en_encoded=dark_en_encoded,
                           en_encode=en_encode,
                           dr_en_encode=dr_en_encode)

#model redirect
@app.route('/predict', methods=['POST'])
def predict():
    """
    The function takes an image file as input, converts it to base64 encoded string, sends it to the
    server, gets the response, converts the response to base64 encoded string and returns it to the
    client
    :return: The return value of the function is the response object.
    """
    if request.method =='POST':
        image_file = request.files['file']
        if not image_file:
            return render_template('error.html', message='Please upload a image file')
         # Get the file extension from the uploaded file
        file_extension = os.path.splitext(image_file.filename)[1].lower()

        if file_extension in ('.jpg', '.jpeg'):
            image_file = Image.open(image_file)
            buffer = io.BytesIO()
            image_file.save(buffer, format='JPEG')
        elif file_extension == '.png':
            image_file = Image.open(image_file)
            buffer = io.BytesIO()
            image_file.save(buffer, format='PNG')
        else:
            # Handle unsupported formats
            return render_template('error.html', message='Unsupported file format only jpg,jpeg and png files supported')

        original_image_bytes = buffer.getvalue()

        encoded_original_image = base64.b64encode(original_image_bytes).decode()

        response_selected = request.form.getlist('response[]')

        if len(response_selected) == 1:
            if response_selected[0] == '1':
                response = requests.post('http://127.0.0.1:8080/enhance',files={'file':original_image_bytes})

                encoded_enhanced_image = response.json()['OutputImage']

                
                
                return render_template('mirnet.html',original_image=encoded_original_image,enhanced_image=encoded_enhanced_image)
            
            elif response_selected[0] == '2':
                response = requests.post('http://127.0.0.1:8080/superimage',files={'image':original_image_bytes})
                encoded_super_image = response.json()['super_image']
            
                enhanced_image_size = response.json()['enhanced_size']
                enhanced_image_size = f'(Height: {enhanced_image_size[0]} px, Width: {enhanced_image_size[1]} px)'



                return render_template('swin2svr1.html',encoded_super_image=encoded_super_image,
                                encoded_original_image=encoded_original_image,
                                    enhanced_image_size=enhanced_image_size)
        
        elif len(response_selected) == 2:
            response1 = requests.post('http://127.0.0.1:8080/enhance',files={'file':original_image_bytes})
            encoded_enhanced_image = response1.json()['OutputImage']
           
            image_bytes = base64.b64decode(encoded_enhanced_image)

            response2 = requests.post('http://127.0.0.1:8080/superimage',files={'image':image_bytes})
            encoded_super_image = response2.json()['super_image']

            encoded_original_image = base64.b64encode(original_image_bytes).decode()

            original_image_size = response2.json()['original_size']
            enhanced_image_size = response2.json()['enhanced_size']
            original_image_size = f'(Height: {original_image_size[0]} px, Width: {original_image_size[1]} px)'
            enhanced_image_size = f'(Height: {enhanced_image_size[0]} px, Width: {enhanced_image_size[1]} px)'


            return render_template('both.html',encoded_super_image=encoded_super_image,
                                    encoded_original_image=encoded_original_image,
                                    original_image_size=original_image_size,
                                    enhanced_image_size=enhanced_image_size
            )
        
        else:
            return render_template('error.html',message = "No options selected, select any one")
        
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)
