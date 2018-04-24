from setuptools import setup

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
    ],
    python_requires='>=3.5',
    install_requires=[
    ],
)
