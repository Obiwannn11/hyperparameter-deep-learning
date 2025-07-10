import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tensorflow as tf
from PIL import Image
import numpy as np
import io

# 1. Inisialisasi Aplikasi Flask
app = Flask(__name__)
CORS(app)

# 2. Konfigurasi Model
# BARU: Path untuk dua model
BEST_MODEL_PATH = os.path.join('static', 'best_model.h5') 
WORST_MODEL_PATH = os.path.join('static', 'worst_model.h5') 

IMG_SIZE = 224
CLASS_NAMES = ['bersih', 'kotor sedang', 'sangat kotor'] 

# 3. Muat Kedua Model TensorFlow
try:
    best_model = tf.keras.models.load_model(BEST_MODEL_PATH)
    worst_model = tf.keras.models.load_model(WORST_MODEL_PATH) # BARU: Muat model kedua
    print("Semua model berhasil dimuat.")
except Exception as e:
    print(f"Error memuat model: {e}")
    best_model = None
    worst_model = None

# 4. Fungsi untuk Pra-pemrosesan Gambar (tidak berubah)
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# 5. Definisikan Rute API untuk Prediksi
@app.route('/predict', methods=['POST'])
def predict():
    if not best_model or not worst_model:
        return jsonify({'error': 'Satu atau lebih model tidak berhasil dimuat'}), 500
        
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang dikirim'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'File tidak dipilih'}), 400

    try:
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)
        
        # BARU: Lakukan prediksi pada kedua model
        prediction_best = best_model.predict(processed_image)
        prediction_worst = worst_model.predict(processed_image)
        
        # BARU: Dapatkan hasil untuk kedua model
        result_best = CLASS_NAMES[np.argmax(prediction_best)]
        result_worst = CLASS_NAMES[np.argmax(prediction_worst)]
        
        # BARU: Kirim kedua hasil dalam satu JSON
        return jsonify({
            'best_prediction': result_best,
            'worst_prediction': result_worst
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# BARU: Rute untuk halaman utama (Tebak Gambar)
@app.route('/')
def tebak_page():
    # Mengambil file tebak.html dari folder templates
    return render_template('tebak.html')

# BARU: Rute untuk halaman Perbandingan Gambar
@app.route('/bandingkan')
def bandingkan_page():
    # Mengambil file bandingkan.html dari folder templates
    return render_template('bandingkan.html')


# 6. Jalankan Aplikasi
if __name__ == '__main__':
    app.run(debug=True, port=5000)