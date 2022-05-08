import os
import sys

# I don't think this will work when we test cli.py because the relative imports...
sys.path.append(f"{os.path.dirname(os.path.dirname(__file__))}/ecomment")
