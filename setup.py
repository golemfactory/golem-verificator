from setuptools import setup
from os import path

setup(
    name='Golem-Verificator',
    version='1.2.1',
    url='https://github.com/golemfactory/golem-vericator',
    maintainer='The Golem team',
    maintainer_email='tech@golem.network',
    packages=[
        'golem_verificator',
        'golem_verificator.common',
        'golem_verificator.docker',
        'golem_verificator.docker.blender.images.scripts'
    ],
    package_dir={'golem_verificator': 'golem_verificator'},
    package_data={'golem_verificator': [ path.normpath(
                                             'docker/blender/images/scripts/runner.py')]},
    python_requires='>=3.5'
)
