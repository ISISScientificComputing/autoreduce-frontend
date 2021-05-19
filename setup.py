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
    version='21.1',
    description='The frontend of the ISIS Autoreduction service',
    author='ISIS Autoreduction Team',
    url='https://github.com/ISISScientificComputing/autoreduce-frontend/',
    install_requires=[
        'autoreduce_utils==0.1.2', 'attrs==21.2.0', 'dash==1.20.0', 'dash_html_components==1.1.3',
        'dash_core_components==1.16.0', 'Django==3.2.2', 'django_extensions==3.1.3', 'django_plotly_dash==1.6.3',
        'django-user-agents==0.4.0', 'python-icat==0.18.1'
    ],
    packages=find_packages(),
)
