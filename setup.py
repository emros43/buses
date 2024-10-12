""" Set up instructions and meta data. """

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='buses',
    version='1.0',
    author='Emilia Rosla',
    author_email="er438696@mimuw.edu.pl",
    description='A bus tracking and analysis program',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
