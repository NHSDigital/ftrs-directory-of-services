import logging
import re

from pipeline import processor

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: any, context: any) -> None:
    logging.info("Executing lambda handler")
    try:
        date = event.get("date")
        if not date:
            return {"statusCode": 400, "body": ("Date parameter is required")}
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, date):
            return {"statusCode": 400, "body": "Date must be in YYYY-MM-DD format"}

        processor(date=event["date"])
    except Exception as e:
        logging.info(f"Unexpected error: {e}")
        return {"statusCode": 500, "body": f"Unexpected error: {e}"}
