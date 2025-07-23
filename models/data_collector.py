import os
import json
from datetime import datetime
import shutil

class DataCollector:
    def __init__(self, base_path='static/training_data'):
        self.base_path = base_path
        self.metadata_file = os.path.join(base_path, 'metadata.json')
        self.initialize_storage()

    def initialize_storage(self):
        # Create directories for different analysis types
        os.makedirs(self.base_path, exist_ok=True)
        for analysis_type in ['classification', 'object_detection', 'sentiment', 'text_extraction']:
            os.makedirs(os.path.join(self.base_path, analysis_type), exist_ok=True)

        # Initialize metadata file if it doesn't exist
        if not os.path.exists(self.metadata_file):
            self._save_metadata({})

    def collect_training_data(self, image_path, analysis_results, query_type, user_feedback=None):
        try:
            # Generate unique ID for the training sample
            sample_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create directory for this sample
            sample_dir = os.path.join(self.base_path, query_type, sample_id)
            os.makedirs(sample_dir, exist_ok=True)

            # Copy image to training data directory
            image_filename = os.path.basename(image_path)
            shutil.copy2(image_path, os.path.join(sample_dir, image_filename))

            # Save analysis results
            with open(os.path.join(sample_dir, 'analysis.json'), 'w') as f:
                json.dump(analysis_results, f, indent=4)

            # Save user feedback if available
            if user_feedback:
                feedback_file = os.path.join(sample_dir, 'feedback.json')
                with open(feedback_file, 'w') as f:
                    json.dump({'feedback': user_feedback}, f, indent=4)

            # Update metadata
            metadata = self._load_metadata()
            metadata[sample_id] = {
                'timestamp': datetime.now().isoformat(),
                'query_type': query_type,
                'image_path': image_filename,
                'status': 'collected'
            }
            self._save_metadata(metadata)

            return True

        except Exception as e:
            print(f"Error collecting training data: {str(e)}")
            return False

    def _load_metadata(self):
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_metadata(self, metadata):
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4) 