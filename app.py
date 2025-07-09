import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from PIL import Image
import numpy as np
import io

# 1. Inisialisasi Aplikasi Flask
app = Flask(__name__)
CORS(app)  # Mengizinkan Cross-Origin Resource Sharing

# 2. Konfigurasi Model
# Pastikan path ini benar sesuai struktur folder Anda
MODEL_PATH = os.path.join('static', 'model_mobilenetv2.h5') 
IMG_SIZE = 224
# Sesuaikan urutan nama kelas ini persis seperti saat Anda melatih model
CLASS_NAMES = ['sangat_bersih', 'sangat_kotor', 'sedang'] 

# 3. Muat Model TensorFlow
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"Model {MODEL_PATH} berhasil dimuat.")
except Exception as e:
    print(f"Error memuat model: {e}")
    model = None

# 4. Fungsi untuk Pra-pemrosesan Gambar
def preprocess_image(image_bytes):
    """
    Fungsi ini mengambil byte gambar, mengubah ukurannya, menormalkannya,
    dan menyiapkannya untuk model.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB') # Pastikan gambar dalam format RGB
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0  # Normalisasi piksel ke rentang [0, 1]
    img_array = np.expand_dims(img_array, axis=0) # Tambah dimensi batch (1, 224, 224, 3)
    return img_array

# 5. Definisikan Rute API untuk Prediksi
@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model tidak berhasil dimuat'}), 500
        
    # Cek apakah ada file yang dikirim dalam request
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang dikirim'}), 400

    file = request.files['file']

    # Cek apakah file memiliki nama (artinya file benar-benar dipilih)
    if file.filename == '':
        return jsonify({'error': 'File tidak dipilih'}), 400

    try:
        # Baca file gambar
        image_bytes = file.read()
        print(f"File {file.filename} berhasil dibaca.")
        
        # Lakukan pra-pemrosesan
        processed_image = preprocess_image(image_bytes)
        
        # Lakukan prediksi
        prediction = model.predict(processed_image)
        print(f"Prediksi berhasil dilakukan untuk {file.filename}.")
        
        # Dapatkan indeks kelas dengan probabilitas tertinggi
        predicted_class_index = np.argmax(prediction)
        print(f"Prediksi selesai untuk {file.filename}.")
        
        # Dapatkan nama kelas dari indeks
        predicted_class_name = CLASS_NAMES[predicted_class_index]
        print(f"Prediksi selesai untuk {file.filename}.")
        
        # Kirim hasil sebagai JSON
        return jsonify({'prediction': predicted_class_name})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 6. Jalankan Aplikasi
if __name__ == '__main__':
    app.run(debug=True, port=5000)