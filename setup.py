# pylint:skip-file
"""
Wrapper for the functionality for various installation and project setup commands
see:
    `python setup.py help`
for more details
"""
from setuptools import setup, find_packages

setup(
    name='autoreduction-frontend',
    version='21.1.1',
    description='The frontend of the ISIS Autoreduction service',
    author='ISIS Autoreduction Team',
    url='https://github.com/ISISScientificComputing/autoreduce-frontend/',
    install_requires=[
        'autoreduce_db==0.1.2', 'autoreduce_utils==0.1.3', 'autoreduce_qp==21.1', 'attrs==21.2.0', 'Django==3.2.2',
        'django_extensions==3.1.3', 'django-user-agents==0.4.0', 'python-icat==0.18.1'
    ],
    packages=find_packages(),
)
