import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, dir_path)

from marthas_dashboard import app as application
application.jinja_env.cache = None
