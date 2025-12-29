from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app) # Cho phép frontend gọi mà không bị lỗi bảo mật

# --- CẤU HÌNH ĐƯỜNG DẪN MODEL ---
# Đảm bảo bạn có thư mục 'models' chứa 2 file .joblib nằm cùng cấp hoặc chỉnh lại path
MODEL_PATH = "models" 
SCALER_FILE = os.path.join(MODEL_PATH, "weather_scaler.joblib")
KMEANS_FILE = os.path.join(MODEL_PATH, "weather_kmeans.joblib")

# Load Models
try:
    scaler = joblib.load(SCALER_FILE)
    kmeans = joblib.load(KMEANS_FILE)
    print("✅ Đã load model thành công!")
except Exception as e:
    print(f"❌ Lỗi load model: {e}")
    scaler = None
    kmeans = None

# Map kết quả cluster sang tiếng Việt/Anh
cluster_map = {
    0: {"label": "Wet (Ẩm ướt/Mưa nhiều)", "color": "#3498db", "icon": "🌧️"},
    1: {"label": "Normal (Ôn hòa)", "color": "#2ecc71", "icon": "🌤️"},
    2: {"label": "Dry (Khô ráo)", "color": "#e67e22", "icon": "🌵"}
}

@app.route('/predict', methods=['POST'])
def predict():
    if not scaler or not kmeans:
        return jsonify({"error": "Model not loaded"}), 500
    try:
        data = request.json
       
        input_df = pd.DataFrame([data])
        
        input_df = input_df[["t_max", "t_min", "wind_speed", "rain"]]

        # Scale dữ liệu
        X_scaled = scaler.transform(input_df)

        # Dự đoán
        cluster_id = kmeans.predict(X_scaled)[0]
        result_info = cluster_map.get(int(cluster_id), {"label": "Unknown", "color": "#fff"})
        print(cluster_id, result_info)

        #T rả về kết quả
        return jsonify({
            "status": "success",
            "cluster_id": int(cluster_id),
            "condition": result_info["label"],
            "color": result_info["color"],
            "icon": result_info["icon"]
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)