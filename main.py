from flask import Flask, render_template, send_from_directory, url_for, session, request
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from flask_wtf.file import FileRequired, FileAllowed

from PIL import Image
import pickle
import numpy as np

app = Flask(__name__)
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
app.config['SECRET_KEY'] = '621ly1ee'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileRequired(),
            FileAllowed(photos, 'Only images are allowed')
        ]
    )
    submit = SubmitField('Upload')

with open('model.pkl', 'rb') as f:
    data = pickle.load(f)

model = data['model']

@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    prediction = None
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        session['filename'] = filename
        file_url = url_for('get_file', filename=filename)
    else:
        file_url = None
    if request.method == 'POST' and request.form.get('action') == 'predict':
        filename = session.get('filename', None)
        img = Image.open(f'uploads/{filename}').resize((28, 28)).convert('L')
        img_array = np.asarray(img).reshape(1, -1)
        prediction = str(int(model.predict(img_array)))
    return render_template('index.html', form=form, file_url=file_url, prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)