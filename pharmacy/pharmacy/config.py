import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DBG = os.getenv("DEBUG") == "True"
TZ = os.getenv("TIME_ZONE", "UTC")
LOW_QTY_THRESHOLD = 0.8
