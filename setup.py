#!/usr/bin/env python3

from setuptools import setup
import unittest

# ./setup.py bdist_egg


def test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


setup(
    name='Golem Verificator',
    version='1.0rc0',
    description='Shared module for verification (Golem and Concent)',
    url='https://github.com/golemfactory/golem-verificator',
    author='golem network',
    author_email='contact@golem.network',
    license="GPL-3.0",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5.2',
    ],
    packages=['golem_verificator'],
    install_requires=[
        'cycler == 0.10.0',
        'decorator == 4.1.2',
        'et-xmlfile == 1.0.1',
        'imutils == 0.4.3',
        'jdcal == 1.3',
        'matplotlib == 2.0.2',
        'networkx == 1.11',
        'numpy == 1.13.1',
        'olefile == 0.44',
        'OpenEXR == 1.3.0',
        'openpyxl == 2.4.8',
        'pandas == 0.20.3',
        'Pillow == 4.2.1',
        'pyparsing == 2.2.0',
        'pyssim == 0.3',
        'python-dateutil == 2.6.1',
        'pytz == 2017.2',
        'PyWavelets == 0.5.2',
        'scikit-image == 0.13.0',
        'scipy',
        'six == 1.10.0',
        'opencv-python',
    ],
    scripts=[
        'golem_verificator/scripts/validation.py'
    ],
    test_suite='setup.test_suite',
    extras_require={
        'test': 'flake8',
    },
)
