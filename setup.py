# pylint:skip-file
"""
Wrapper for the functionality for various installation and project setup commands
see:
    `python setup.py help`
for more details
"""
from setuptools import setup, find_packages

setup(name="autoreduce_webapp",
      version="21.1.1",
      description="The frontend of the ISIS Autoreduction service",
      author="ISIS Autoreduction Team",
      url="https://github.com/ISISScientificComputing/autoreduce-frontend/",
      install_requires=[
          "autoreduce_utils==0.1.3", "autoreduce_db==0.1.4", "autoreduce_qp==21.1.3", "Django==3.2.2",
          "django_extensions==3.1.3", "django-user-agents==0.4.0"
      ],
      packages=find_packages(),
      entry_points={"console_scripts": ["autoreduce-webapp-manage = autoreduce_webapp.manage:main"]})
