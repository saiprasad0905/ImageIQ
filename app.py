from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from PIL import Image
import google.generativeai as genai
import numpy as np
import logging
import os
from werkzeug.utils import secure_filename
from models.ensemble import (
    ImageClassificationEnsemble, 
    ObjectDetectionEnsemble, 
    SentimentEnsemble,
    TextExtractionEnsemble
)
from datetime import datetime
from models.data_collector import DataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)

class MLModels:
    def __init__(self):
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.image_classifier = self._init_with_retry(ImageClassificationEnsemble)
            self.object_detector = self._init_with_retry(ObjectDetectionEnsemble)
            self.sentiment_analyzer = self._init_with_retry(SentimentEnsemble)
            self.text_extractor = self._init_with_retry(TextExtractionEnsemble)
            self.data_collector = DataCollector()
            logger.info("ML models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ML models: {str(e)}")
            raise

    def get_gemini_response(self, prompt, image):
        try:
            # Ensure prompt is not empty
            if not prompt:
                logger.warning("Prompt is empty, generating content with image only.")
                prompt = "Please analyze the image."  # Default prompt if none is provided

            # Attempt to generate content using the Gemini API
            response = self.gemini_model.generate_content([prompt, image])

            # Check if response is valid
            if response and hasattr(response, 'text'):
                logger.info("Gemini API response generated successfully.")
                return response.text
            else:
                logger.error("Invalid response from Gemini API.")
                raise ValueError("Invalid response from Gemini API.")
        except Exception as e:
            logger.error(f"Gemini model error: {str(e)}")
            raise

    def _init_with_retry(self, model_class, max_retries=3):
        for attempt in range(max_retries):
            try:
                return model_class()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Retry {attempt + 1} for {model_class.__name__}: {str(e)}")

# Add these configurations
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ml_models = MLModels()  # Create an instance of MLModels

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        image_file = request.files.get('image')
        query_type = request.form.get('query_type', 'general')
        text_input = request.form.get('input', '')

        if not image_file or not allowed_file(image_file.filename):
            logger.error('Invalid or missing image file')
            return jsonify({'error': 'Invalid or missing image file'}), 400

        # Save the uploaded file with timestamp
        filename = secure_filename(image_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        # Save the file
        image_file.save(filepath)

        # Process image
        try:
            image = Image.open(filepath).convert('RGB')
            if image.size[0] > 4096 or image.size[1] > 4096:
                image = image.resize((4096, 4096), Image.Resampling.LANCZOS)
                image.save(filepath)
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return jsonify({'error': f'Image processing error: {str(e)}'}), 400

        results = {
            'query_type': query_type,
            'analysis': {},
            'image_path': f'/static/uploads/{unique_filename}',
            'user_feedback': request.form.get('user_feedback', '')
        }

        # Analyze the image content
        try:
            if query_type == 'general':
                prompt = text_input if text_input else "Analyze this image in detail."
                gemini_response = ml_models.get_gemini_response(prompt, image)
                results['analysis']['gemini_response'] = gemini_response

            elif query_type == 'classification':
                classifications = ml_models.image_classifier.predict(image)
                results['analysis']['classification'] = {'predictions': classifications}

            elif query_type == 'object_detection':
                object_detections = ml_models.object_detector.detect(image)
                results['analysis']['objects'] = object_detections

            elif query_type == 'sentiment':
                text_input = request.form.get('input', '')  # Make text input optional
                sentiment = ml_models.sentiment_analyzer.analyze(image, text_input if text_input else None)
                results['analysis']['sentiment'] = sentiment['ensemble_prediction']

            elif query_type == 'text_extraction':
                extracted_text = ml_models.text_extractor.extract(image)
                results['analysis']['extracted_text'] = extracted_text

            else:
                return jsonify({'error': 'Invalid query type'}), 400

            return jsonify(results)

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

    except Exception as e:
        logger.error(f"Request processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.before_request
def log_request_info():
    logger.info(f"Request Path: {request.path}, Method: {request.method}")

@app.route('/test_gemini', methods=['POST'])
def test_gemini():
    prompt = request.form.get('prompt', 'Analyze this image.')
    image_file = request.files.get('image')

    if not image_file or not allowed_file(image_file.filename):
        return jsonify({'error': 'Invalid or missing image file'}), 400

    # Save the uploaded file temporarily
    filename = secure_filename(image_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(filepath)

    try:
        image = Image.open(filepath).convert('RGB')
        response_text = ml_models.get_gemini_response(prompt, image)
        return jsonify({'response': response_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)