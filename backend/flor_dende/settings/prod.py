from .base import *
from decouple import config
DEBUG = False
CORS_ALLOWED_ORIGINS = config('CORS_ORIGINS', default='http://localhost:5173').split(',')
