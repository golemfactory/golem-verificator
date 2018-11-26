from setuptools import setup

setup(
    name='Golem-Verificator',
    version='1.6.2',
    url='https://github.com/golemfactory/golem-verificator',
    maintainer='The Golem Team',
    maintainer_email='tech@golem.network',
    packages=[
        'golem_verificator',
        'golem_verificator.common',
        'golem_verificator.docker',
        'golem_verificator.docker.blender.images.scripts',
        'golem_verificator.docker.blender.images.scripts.metrics'
    ],
    package_dir={'golem_verificator': 'golem_verificator'},
    python_requires='>=3.5'
)
