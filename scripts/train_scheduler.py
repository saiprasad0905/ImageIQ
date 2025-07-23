import schedule
import time
from models.trainer import ModelTrainer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_models():
    try:
        trainer = ModelTrainer()
        trainer.train()
        logger.info("Scheduled training completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled training: {str(e)}")

def main():
    # Schedule training to run daily at midnight
    schedule.every().day.at("00:00").do(train_models)
    
    logger.info("Training scheduler started")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 