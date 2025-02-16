# app.py
from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import cv2
import numpy as np

model = joblib.load('artifact_model.pkl')
artifact_info = pd.read_csv('artifact_info.csv')

app = Flask(__name__, static_folder='static', template_folder='templates')

def preprocess_image(image):
    image = cv2.resize(image, (64, 64)).flatten() 
    return image.reshape(1, -1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rajasthan')
def rajasthan():
    return render_template('rajasthan.html')


@app.route('/uttar_pradesh')
def uttar_pradesh():
    return render_template('uttar_pradesh.html')


@app.route('/tamil_nadu')
def tamil_nadu():
    return render_template('tamil_nadu.html')


@app.route('/maharashtra')
def maharashtra():
    return render_template('maharashtra.html')


@app.route('/andhra_pradesh')
def andhra_pradesh():
    return render_template('andhra_pradesh.html')

@app.route('/ar_page')
def ar_page():
    return render_template('ar_page.html')

@app.route('/webcam')
def webcam():
    return render_template('webcam.html') 


@app.route('/api/upload/', methods=['POST'])
def classify_image():
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    processed_image = preprocess_image(image)

    
    class_probabilities = model.predict_proba(processed_image)  # Check if your model supports this
    class_id = model.predict(processed_image)[0]
    confidence = max(class_probabilities[0]) if class_probabilities is not None else None

    
    print(f"Predicted class_id: {class_id}, Confidence: {confidence}")
    print(f"Available IDs in CSV: {artifact_info['id'].unique()}")

    
    class_id = str(class_id)
    artifact_info['id'] = artifact_info['id'].astype(str).str.strip()

    
    artifact_details = artifact_info[artifact_info['id'] == class_id].to_dict(orient='records')

    
    print("Fetched artifact details:", artifact_details)

    if artifact_details:
        response = {
            'predicted_class': artifact_details[0].get('artifacts_name', 'N/A'),
            'description': artifact_details[0].get('description', 'N/A'),
            'historical_significance': artifact_details[0].get('historical_significance', 'N/A'),
            'origin': artifact_details[0].get('origin', 'N/A'),
            'confidence': confidence
        }
        
        if confidence and confidence < 0.6:  
            response['warning'] = 'Low confidence in prediction.'
        return jsonify(response)
    else:
        print(f"Error: Predicted class_id {class_id} does not match any in CSV")
        return jsonify({'error': f'No matching artifact found for class_id {class_id}'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=8000)
