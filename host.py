import uuid
import os

from flask import Flask, send_from_directory
from salvador import generate_from_model
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
port = int(os.environ.get("PORT", 5000))

@app.route('/')
def hello():
    return 'hello world'

@app.route('/generated/<user_id>/<path:filename>')
def download_file(user_id, filename):
    return send_from_directory(f'{user_id}/', filename, as_attachment=True)


@app.route('/generate')
def generate_images():
    user_id = uuid.uuid4().hex
    generate_from_model('models/generator_model_009.h5', dst_catalog=user_id, n_images=1)
    return user_id

app.run(host='0.0.0.0', port=port)