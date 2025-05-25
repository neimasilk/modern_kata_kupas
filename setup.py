from setuptools import setup, find_packages
import os

# Function to read the content of README.md for long_description
def read_readme():
    try:
        # Assuming setup.py is in the root directory with README.md
        with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback description if README is not found during build
        return "Modern Indonesian Morphological Separator and Reconstructor. See URL for full details."

setup(
    name='modern_kata_kupas',
    version='1.0.0',
    author='Tim ModernKataKupas',
    author_email='kontak@modernkatakupas.id', # Placeholder email
    description='Modern Indonesian Morphological Separator and Reconstructor for V1.0',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/neimasilk/modern_kata_kupas', # Actual project URL
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'modern_kata_kupas': ['data/*.txt', 'data/*.json'],
    },
    install_requires=[
        'PySastrawi>=1.2.0,<2.0.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Indonesian',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Text Processing :: Linguistic',
        'Operating System :: OS Independent',
    ],
    keywords='indonesian morphology nlp linguistic text processing kata kupas morpheme segmenter reconstructor',
)