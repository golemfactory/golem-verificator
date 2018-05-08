from setuptools import setup
from os import path

setup(
    name='Golem-Verificator',
    version='1.0.0',
    url='https://github.com/golemfactory/golem-vericator',
    maintainer='The Golem team',
    maintainer_email='tech@golem.network',
    packages=[
        'golem_verificator',
        'golem_verificator.common',
        'golem_verificator.docker',
        'golem_verificator.docker.blender.images.scripts',
    ],
    data_files = [
        (path.normpath('common'), [
            path.normpath('golem_verificator/common/blendercrop.py.template'),
        ])
    ],
    python_requires='>=3.5'
)
