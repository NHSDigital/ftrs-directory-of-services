import logging
import sys

from pipeline.processor import extract

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
CORRECT_LENGTH = 2

if len(sys.argv) != CORRECT_LENGTH:
    print("Usage: python cli.py YYYY-MM-DD")
    sys.exit(1)

date = sys.argv[1]
extract(date=date)
