import google.generativeai as genai
from PIL import Image
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class TextExtractionEnsemble:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Text Extraction Ensemble initialized")
        except Exception as e:
            logger.error(f"Error initializing text extraction: {str(e)}")
            raise

    def extract(self, image):
        try:
            prompt = """
            Extract all text visible in this image. Format the response as follows:
            - Include only the text found in the image
            - Separate different text blocks with line breaks
            - Do not include any analysis or commentary
            - Return only the extracted text
            """
            response = self.model.generate_content([prompt, image])
            extracted_text = response.text.strip()
            
            return {
                'printed_text': extracted_text,
                'handwritten_text': '',
                'text_regions': []
            }
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}")
            raise

class ImageClassificationEnsemble:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Image Classification Ensemble initialized")
        except Exception as e:
            logger.error(f"Error initializing image classification: {str(e)}")
            raise

    def predict(self, image):
        try:
            prompt = """
            Provide a detailed classification analysis of this image. Include:

            1. PRIMARY SUBJECT:
            - Main subject or focus of the image
            - Category or type classification
            
            2. SCENE CLASSIFICATION:
            - Environment/setting type
            - Time of day/lighting conditions
            - Indoor/outdoor classification
            
            3. STYLE & COMPOSITION:
            - Photographic/artistic style
            - Color scheme
            - Composition type
            
            4. TECHNICAL DETAILS:
            - Image quality assessment
            - Notable technical aspects
            
            5. ADDITIONAL CATEGORIES:
            - Genre or specific category
            - Relevant tags or keywords
            
            Format the response with clear section headers and bullet points.
            """
            
            response = self.model.generate_content([prompt, image])
            logger.info(f"Advanced classification response: {response.text}")
            
            # Parse the response into structured format
            analysis = response.text.strip()
            sections = analysis.split('\n\n')
            
            # Create structured output
            classification_result = {
                'primary_subject': [],
                'scene_classification': [],
                'style_composition': [],
                'technical_details': [],
                'additional_categories': []
            }
            
            current_section = None
            for section in sections:
                if 'PRIMARY SUBJECT:' in section:
                    items = section.replace('PRIMARY SUBJECT:', '').strip().split('\n')
                    classification_result['primary_subject'] = [item.strip().replace('-', '').strip() 
                                                             for item in items if item.strip()]
                elif 'SCENE CLASSIFICATION:' in section:
                    items = section.replace('SCENE CLASSIFICATION:', '').strip().split('\n')
                    classification_result['scene_classification'] = [item.strip().replace('-', '').strip() 
                                                                  for item in items if item.strip()]
                elif 'STYLE & COMPOSITION:' in section:
                    items = section.replace('STYLE & COMPOSITION:', '').strip().split('\n')
                    classification_result['style_composition'] = [item.strip().replace('-', '').strip() 
                                                               for item in items if item.strip()]
                elif 'TECHNICAL DETAILS:' in section:
                    items = section.replace('TECHNICAL DETAILS:', '').strip().split('\n')
                    classification_result['technical_details'] = [item.strip().replace('-', '').strip() 
                                                               for item in items if item.strip()]
                elif 'ADDITIONAL CATEGORIES:' in section:
                    items = section.replace('ADDITIONAL CATEGORIES:', '').strip().split('\n')
                    classification_result['additional_categories'] = [item.strip().replace('-', '').strip() 
                                                                   for item in items if item.strip()]
            
            return classification_result
            
        except Exception as e:
            logger.error(f"Error in image classification: {str(e)}")
            raise

class ObjectDetectionEnsemble:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Object Detection Ensemble initialized")
        except Exception as e:
            logger.error(f"Error initializing object detection: {str(e)}")
            raise

    def detect(self, image):
        try:
            prompt = """
            Analyze this image in detail and provide:
            1. List all objects present in the image
            2. Categorize objects into:
               - Main subjects
               - Background elements
               - Notable details
            3. Describe spatial relationships between objects
            4. Identify any distinctive features or patterns
            
            Format the response as follows:
            MAIN OBJECTS:
            [List main objects]
            
            BACKGROUND:
            [List background elements]
            
            DETAILS:
            [List notable details]
            
            RELATIONSHIPS:
            [Describe spatial relationships]
            
            DISTINCTIVE FEATURES:
            [List distinctive features]
            """
            
            response = self.model.generate_content([prompt, image])
            logger.info(f"Advanced object detection response: {response.text}")
            
            # Parse the response into structured format
            analysis = response.text.strip()
            sections = analysis.split('\n\n')
            
            # Create structured output
            structured_analysis = {
                'main_objects': [],
                'background': [],
                'details': [],
                'relationships': '',
                'distinctive_features': []
            }
            
            current_section = None
            for section in sections:
                if 'MAIN OBJECTS:' in section:
                    current_section = 'main_objects'
                    items = section.replace('MAIN OBJECTS:', '').strip().split('\n')
                    structured_analysis['main_objects'] = [item.strip() for item in items if item.strip()]
                elif 'BACKGROUND:' in section:
                    current_section = 'background'
                    items = section.replace('BACKGROUND:', '').strip().split('\n')
                    structured_analysis['background'] = [item.strip() for item in items if item.strip()]
                elif 'DETAILS:' in section:
                    current_section = 'details'
                    items = section.replace('DETAILS:', '').strip().split('\n')
                    structured_analysis['details'] = [item.strip() for item in items if item.strip()]
                elif 'RELATIONSHIPS:' in section:
                    current_section = 'relationships'
                    structured_analysis['relationships'] = section.replace('RELATIONSHIPS:', '').strip()
                elif 'DISTINCTIVE FEATURES:' in section:
                    current_section = 'distinctive_features'
                    items = section.replace('DISTINCTIVE FEATURES:', '').strip().split('\n')
                    structured_analysis['distinctive_features'] = [item.strip() for item in items if item.strip()]
            
            return structured_analysis
            
        except Exception as e:
            logger.error(f"Error in object detection: {str(e)}")
            raise

class SentimentEnsemble:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Sentiment Ensemble initialized")
        except Exception as e:
            logger.error(f"Error initializing sentiment analysis: {str(e)}")
            raise

    def analyze(self, image, text=None):
        try:
            if text:
                prompt = f"""
                Provide a detailed sentiment analysis of the following text. Include:
                Text: {text}
                """
            else:
                prompt = """
                Analyze the emotional content and mood of this image. Include:

                1. OVERALL SENTIMENT:
                - Primary emotion/mood (POSITIVE, NEGATIVE, or NEUTRAL)
                - Emotional intensity level
                - Visual mood indicators
                
                2. EMOTIONAL COMPONENTS:
                - List specific emotions conveyed
                - Key visual emotional triggers
                - Mood-setting elements
                
                3. CONTEXTUAL ANALYSIS:
                - Visual tone and atmosphere
                - Color psychology
                - Compositional mood elements
                
                4. SEMANTIC INSIGHTS:
                - Emotional themes
                - Symbolic elements
                - Overall emotional impact

                Format the response with clear section headers and bullet points.
                """
            
            response = self.model.generate_content([prompt, image] if not text else prompt)
            analysis = response.text.strip()
            sections = analysis.split('\n\n')
            
            # Create structured output
            sentiment_analysis = {
                'overall_sentiment': {
                    'primary_emotion': 'NEUTRAL',
                    'intensity': 'moderate',
                    'confidence': '100%'
                },
                'emotional_components': [],
                'contextual_analysis': [],
                'semantic_insights': []
            }
            
            # Parse sections
            for section in sections:
                if 'OVERALL SENTIMENT:' in section:
                    items = section.replace('OVERALL SENTIMENT:', '').strip().split('\n')
                    for item in items:
                        if 'POSITIVE' in item.upper():
                            sentiment_analysis['overall_sentiment']['primary_emotion'] = 'POSITIVE'
                        elif 'NEGATIVE' in item.upper():
                            sentiment_analysis['overall_sentiment']['primary_emotion'] = 'NEGATIVE'
                        if 'intensity' in item.lower():
                            sentiment_analysis['overall_sentiment']['intensity'] = item.split(':')[-1].strip()
                
                elif 'EMOTIONAL COMPONENTS:' in section:
                    items = section.replace('EMOTIONAL COMPONENTS:', '').strip().split('\n')
                    sentiment_analysis['emotional_components'] = [
                        item.strip().replace('-', '').strip() 
                        for item in items if item.strip()
                    ]
                
                elif 'CONTEXTUAL ANALYSIS:' in section:
                    items = section.replace('CONTEXTUAL ANALYSIS:', '').strip().split('\n')
                    sentiment_analysis['contextual_analysis'] = [
                        item.strip().replace('-', '').strip() 
                        for item in items if item.strip()
                    ]
                
                elif 'SEMANTIC INSIGHTS:' in section:
                    items = section.replace('SEMANTIC INSIGHTS:', '').strip().split('\n')
                    sentiment_analysis['semantic_insights'] = [
                        item.strip().replace('-', '').strip() 
                        for item in items if item.strip()
                    ]
            
            return {
                'ensemble_prediction': sentiment_analysis,
                'individual_predictions': {
                    'gemini': {
                        'label': sentiment_analysis['overall_sentiment']['primary_emotion'],
                        'score': 1.0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            raise