import sys
import os
DIR=os.path.dirname(__file__)
sys.path.append(DIR)
sys.path.insert(0, '/home/h0/nsota/myapp/')
from run import app as application