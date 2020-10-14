#!/usr/bin/env python
# -*- coding: utf-8 -*-
# template by kennethreitz: https://github.com/kennethreitz/setup.py
import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'essay-evaluation'
DESCRIPTION = 'Tools for evaluating essays written by language learners.'
URL = 'https://github.com/elia-idp/essayevaluation'
EMAIL = 'hello@meetelia.com'
AUTHOR = 'Aldi Topalli & Simon Klimek'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '1.0.0'

# What packages are required for this module to be executed?
REQUIRED = [
    'hunspell',
    'lexical-diversity',
    'lexicalrichness',
    'neo4j',
    'neuralcoref',
    'nltk',
    'numpy',
    'pandas',
    'Pyphen',
    'scikit-learn',
    'spacy==2.1.3',
    'textblob'
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=[
        "tests", "*.tests", "*.tests.*", "tests.*", "DataReader", "notebooks", "notebooks.notebook_utils", \
        "notebooks.essay_evaluation", "notebooks.essay_evaluation.legacy", "notebooks.DataReader"
    ]),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)


