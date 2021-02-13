import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, Response
from werkzeug.utils import secure_filename
from glass_to_eye import AddGlassToEye, gen

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video/')
def small_frame():
    return Response(gen(AddGlassToEye()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/image/')
def upload_form():
    return render_template('image.html')

@app.route('/image/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_image filename: ' + filename)
        AddGlassToEye().add_glass_to_image(app.config['UPLOAD_FOLDER'], filename)
        return redirect(url_for('static', filename='processed/' + filename))
        # return render_template('upload.html', filename=filename)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='processed/' + filename))

if __name__ == "__main__":
    app.run()