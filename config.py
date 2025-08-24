class Config:
    # Flask app configuration
    FLASK_APP = "app.py"
    FLASK_RUN_HOST = "127.0.0.1"
    FLASK_RUN_PORT = 5001
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = "sqlite:///mechanic_shop.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "supersecretkey123"  

    # Optional: rate limit + cache
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_DEFAULT = "10 per minute"
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60

# Set Flask app name for flask run command
FLASK_APP = "app.py"
