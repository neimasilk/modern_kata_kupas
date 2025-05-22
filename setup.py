from setuptools import setup, find_packages

setup(
    name='modern_kata_kupas',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'modern_kata_kupas.data': ['*.txt', '*.json', 'affix_rules.json'],
    },
    install_requires=[
        # dependensi Anda, jika ada
    ],
)