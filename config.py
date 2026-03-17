import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    JSON_SORT_KEYS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-kitsu-key")
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    

    UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
    UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    
    # Cache durations
    DEFAULT_STALE_WHILE_REVALIDATE = 600  
    MANIFEST_DURATION = 3600  
    CATALOG_ON_SUCCESS_DURATION = 300  
    CATALOG_STALE_WHILE_REVALIDATE = 300
