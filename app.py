import uuid
import os
import json
import gc

from flask import Flask, send_from_directory
from salvador import generate_from_model
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
port = int(os.environ.get("PORT", 5000))

@app.route('/')
def hello():
    return '<meta http-equiv="refresh" content="0; URL=https://adacienciala.github.io/Salvador/webpage/index.html" />'

@app.route('/generated/<user_id>/<path:filename>')
def download_file(user_id, filename):
    return send_from_directory(f'{user_id}/', filename, as_attachment=False)

@app.route('/generated/<user_id>/download-<path:filename>')
def download_file(user_id, filename):
    return send_from_directory(f'{user_id}/', filename, as_attachment=True)

@app.route('/generate')
def generate_images():
    user_id = uuid.uuid4().hex
    generate_from_model('models/generator_model_649.h5', dst_catalog=user_id, n_images=1)
    gc.collect()
    return user_id

@app.route('/slider_images')
def getImagesFilenames():
    return json.dumps(os.listdir('webpage/images/generated_images'))

app.run(host='0.0.0.0', port=port)