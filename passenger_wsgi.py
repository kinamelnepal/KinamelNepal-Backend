import sys
import os

# Add project path
sys.path.insert(0, os.path.dirname(__file__))

from app.wsgi import application  # app = your project folder
