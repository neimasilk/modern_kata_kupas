import sys
import os

# Add the 'src' directory to sys.path
# This allows pytest to find the 'modern_kata_kupas' package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
