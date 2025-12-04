from setuptools import setup, find_packages

setup(
    name='smelly_python',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'smelly_python=smelly_python.main:main',
        ],
    },
)
