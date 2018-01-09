import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

activate_this = dir_path+'/venvs/marthas_dashboard/bin/activate'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, dir_path)

from marthas_dashboard import app as application