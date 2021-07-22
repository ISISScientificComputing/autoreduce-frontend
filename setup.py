# pylint:skip-file
"""
Wrapper for the functionality for various installation and project setup commands
see:
    `python setup.py help`
for more details
"""
from setuptools import setup, find_packages
from glob import glob
import os

PACKAGE_NAME = "autoreduce_frontend"

data_locations = [f"{PACKAGE_NAME}/templates/", f"{PACKAGE_NAME}/static/"]

data_files = []

for loc in data_locations:
    data_files.extend([f.split(f"{PACKAGE_NAME}/")[1] for f in glob(f"{loc}/**", recursive=True) if os.path.isfile(f)])
print(data_files)

setup(name=PACKAGE_NAME,
      version="22.0.0.dev0",
      description="The frontend of the ISIS Autoreduction service",
      author="ISIS Autoreduction Team",
      url="https://github.com/ISISScientificComputing/autoreduce-frontend/",
      install_requires=[
          "autoreduce_utils==22.0.0.dev3", "autoreduce_db==22.0.0.dev4", "autoreduce_qp==22.0.0.dev2", "Django==3.2.4",
          "django_extensions==3.1.3", "django-user-agents==0.4.0", "djangorestframework==3.12.4"
      ],
      packages=find_packages(),
      package_data={"": data_files},
      entry_points={"console_scripts": ["autoreduce-webapp-manage = autoreduce_frontend.manage:main"]})
