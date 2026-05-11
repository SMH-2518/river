import os
import numpy as np
import joblib
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tensorflow as tf

# Reduce TensorFlow memory usage for Render Free Tier
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)

# Point to the 'dist' folder where React build lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'dist'))
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/')
CORS(app)

# Note: Ensure these filenames match your actual files in the folder!
MODEL_PATH = os.path.join(BASE_DIR, "model_epoch_10_direct.keras")
X_SCALER_PATH = os.path.join(BASE_DIR, "x_scaler.pkl")
Y_SCALER_PATH = os.path.join(BASE_DIR, "y_scaler.pkl")

# Load model and scalers
model = tf.keras.models.load_model(MODEL_PATH)
x_scaler = joblib.load(X_SCALER_PATH)
y_scaler = joblib.load(Y_SCALER_PATH)

FEATURE_KEYS = [
    'month', 'day_of_year', 'streamflow_today_cumecs', 'streamflow_anomaly_zscore',
    'flow_rate_of_change', 'flow_velocity_km_per_day', 'antecedent_rain_3d_sum',
    'antecedent_rain_7d_sum', 'antecedent_rain_15d_sum', 'antecedent_rain_30d_sum',
    'antecedent_rain_60d', 'antecedent_rain_ewm', 'rainfall_anomaly_zscore',
    'upstream_rain_mean_scaled', 'upstream_rain_weighted_scaled', 'upstream_rain_lagged_dist_sink',
    'soil_saturation_score', 'antecedent_saturation_interaction', 'is_post_monsoon_saturated',
    'monsoon_intensity', 'monsoon_cumulative_rain', 'dist_to_outlet_scaled', 'upstream_area_scaled',
    'slope_scaled', 'slope_uav_scaled', 'forest_cover_scaled', 'urban_cover_scaled',
    'rain_soilmoisture_interaction', 'rain_urban_interaction', 'rain_slope_interaction',
    'rain_basinsize_interaction', 'uparea_rain_interaction'
]

# --- ROUTE TO SERVE REACT FRONTEND ---
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

# --- PREDICTION API ---
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        features = [float(data[key]) for key in FEATURE_KEYS]
        
        SCALED_KEYS = [
            'streamflow_today_cumecs', 'flow_rate_of_change', 'flow_velocity_km_per_day',
            'antecedent_rain_3d_sum', 'antecedent_rain_7d_sum', 'antecedent_rain_15d_sum',
            'antecedent_rain_30d_sum', 'antecedent_rain_60d', 'antecedent_rain_ewm',
            'monsoon_cumulative_rain', 'monsoon_intensity'
        ]
        
        features_to_scale = [float(data[k]) for k in SCALED_KEYS]
        scaled_sub_array = x_scaler.transform(np.array(features_to_scale).reshape(1, -1))[0]
        
        input_data = np.array(features, dtype=np.float32)
        for i, key in enumerate(SCALED_KEYS):
            input_data[FEATURE_KEYS.index(key)] = scaled_sub_array[i]
            
        input_data = input_data.reshape(1, -1)
        scaled_prediction = model.predict(input_data, verbose=0)
        predicted_value_array = y_scaler.inverse_transform(scaled_prediction)
        
        predicted_delta = float(predicted_value_array.flatten()[0])
        final_prediction = max(0.0, float(data['streamflow_today_cumecs']) + predicted_delta)
        
        return jsonify({'value': final_prediction, 'delta': predicted_delta})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use PORT env variable for Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)