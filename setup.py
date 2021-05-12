# pylint:skip-file
"""
Wrapper for the functionality for various installation and project setup commands
see:
    `python setup.py help`
for more details
"""
from setuptools import setup

setup_requires = [
    'autoreduce_utils==0.1.2', 'attrs==21.2.0', 'dash==1.20.0', 'dash_html_components==1.1.3',
    'dash_core_components==1.16.0', 'Django==3.2.2', 'django_extensions==3.1.3', 'django_plotly_dash==1.6.3',
    'django-user-agents==0.4.0', 'filelock==3.0.12', 'fire==0.4.0', 'gitpython==3.1.14', 'nexusformat==0.6.1',
    'python-icat==0.18.1', 'requests==2.25.1', 'service_identity==21.1.0', 'stomp.py==6.1.0', 'suds-py3==1.4.4.1',
    'PyYAML==5.4.1'
]

setup(
    name='autoreduction-frontend',
    version='21.1',
    description='The frontend of the ISIS Autoreduction service',
    author='ISIS Autoreduction Team',
    url='https://github.com/ISISScientificComputing/autoreduce-frontend/',
    install_requires=setup_requires,
)
