import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DBG = os.getenv("DEBUG") == "True"
TZ = os.getenv("TIME_ZONE", "UTC")
LOW_QTY_THRESHOLD = float(os.getenv("LOW_QTY_THRESHOLD", 0.8))
MAX_DISCOUNT_PERCENTAGE = int(os.getenv("MAX_DISCOUNT_PERCENTAGE", 10))
ONLY_SUPER_USER_CANCEL_ORDER = os.getenv("ONLY_SUPER_USER_CANCEL_ORDER") == "True"
