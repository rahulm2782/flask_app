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
    The function takes the image file and converts it into a string of bytes
    :return: The index.html file is being returned and the image is passed as icon image for models in index.html.
    """
    dark_image_encode = functions.buffer('./images/ying-modified.png')
    both_image_encode = functions.buffer('./images/img_en_.png')
    return render_template('index.html',dark_image_encode=dark_image_encode,
                           both_image_encode=both_image_encode)
#about page
@app.route('/about')
def about():
    """
    It takes the image files and encodes them into a string.
    :return: the image which are actual sample of model outputs shall be returned to the about page.
    """
    dark_en_encoded = functions.buffer('./images/dark.png')
    en_encode = functions.buffer('./images/en.png')
    dr_en_encode = functions.buffer('./images/dk_en.png')
    return render_template('about.html',dark_en_encoded=dark_en_encoded,
                           en_encode=en_encode,
                           dr_en_encode=dr_en_encode)

#model redirect
@app.route('/predict', methods=['POST'])
def predict():
    """
    It takes an image file from the user, sends it to the server, gets the response, and renders the
    response in the browser
    :return: Returns the response as per the model selected by the user.
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

            #Dark image enhancer model
            if response_selected[0] == '1':
                #request sent to dark image enhancer 
                response = requests.post('http://127.0.0.1:8080/enhance',files={'file':original_image_bytes}) #image in form of bytes are sent

                try:
                    encoded_enhanced_image = response.json()['OutputImage']   #response output a json file with image as string encoded 

                    #return original image encoded as tring with the model output in mirnet webpage to be used for side by side comparission
                    return render_template('mirnet.html',original_image=encoded_original_image,enhanced_image=encoded_enhanced_image)
                except:
                    return render_template('error.html',message="Sorry! Something went wrong, try a different image")
            #Low resolution image enhancer model
            elif response_selected[0] == '2':

                #request sent through api
                response = requests.post('http://127.0.0.1:8080/superimage',files={'image':original_image_bytes}) 
                    
                try:    
                    encoded_super_image = response.json()['super_image']     #output image in byte format
                    enhanced_image_size = response.json()['enhanced_size']   #size of the enhanced image as a list [height, width]


                    enhanced_image_size = f'(Height: {enhanced_image_size[0]} px, Width: {enhanced_image_size[1]} px)' #size of enhanced image as string

                    #sending encoded output image and size
                    return render_template('swin2sr.html',encoded_super_image=encoded_super_image,
                                        enhanced_image_size=enhanced_image_size)  #string sent to web page of the model swinsr
                except:
                    return render_template('error.html',message="Sorry! Something went wrong, try a different image")    
        
        #Combined model
        elif len(response_selected) == 2:
            #when user selects both option 1 and 2 that is both models working simultaneously
            response1 = requests.post('http://127.0.0.1:8080/enhance',files={'file':original_image_bytes}) #sending original image as bytes as a request to model darkimage enhancer
            try:
                encoded_enhanced_image = response1.json()['OutputImage'] #output from model as string
            
                image_bytes = base64.b64decode(encoded_enhanced_image)  #decoding string to bytes

                response2 = requests.post('http://127.0.0.1:8080/superimage',files={'image':image_bytes}) #loading the output from dark image enhancer model to low resolution enhancer model
                encoded_super_image = response2.json()['super_image'] #image output from model as string

                encoded_original_image = base64.b64encode(original_image_bytes).decode()  

               # Getting the size of the image and converting it into a string.
                original_image_size = response2.json()['original_size']  #size of original image as list [height, width]
                enhanced_image_size = response2.json()['enhanced_size']
                original_image_size = f'(Height: {original_image_size[0]} px, Width: {original_image_size[1]} px)'
                enhanced_image_size = f'(Height: {enhanced_image_size[0]} px, Width: {enhanced_image_size[1]} px)'



                # Returning the template file both.html with the parameters encoded_super_image,
                # encoded_original_image, original_image_size, enhanced_image_size.

                return render_template('both.html',encoded_super_image=encoded_super_image,
                                        encoded_original_image=encoded_original_image,
                                        original_image_size=original_image_size,
                                        enhanced_image_size=enhanced_image_size)
            
            except:
                return render_template('error.html',message="Sorry! Something went wrong, try a different image")
        
        else:
            return render_template('error.html',message = "No options selected, select any one")
        
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)
