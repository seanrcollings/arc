import sys
from arc.config import configure

configure(environment="development")
sys.argv = ["pytest"]
