from setuptools import setup, find_packages
from os import path
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyhasura',
    version='0.1',
    description='Hasura API client library for Python',
    long_description=long_description,
    url='https://github.com/benhur98/pyhasura',
    author='BENHUR RODRIGIUEZ',
    author_email='benhurrodriguez98@gmail.com',
    license='MIT',
    keywords='hasura python sdk',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'requests'    
    ]
)
