import os
import sys

from app.wsgi import application  # type: ignore

# Add project path
sys.path.insert(0, os.path.dirname(__file__))
print(application)
