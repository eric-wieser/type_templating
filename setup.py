#!/usr/bin/env python
from setuptools import setup, find_packages
import os

version_path = os.path.join('type_templating', '_version.py')
exec(open(version_path).read())

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='type_templating',
    version=__version__,  # noqa: F821
    license='MIT',
    description="C++-style type templating for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Eric Wieser',
    url='http://type_templating.readthedocs.io',
    packages=find_packages(),
    package_dir={'type_templating': 'type_templating'},

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    project_urls={
        "Bug Tracker": "https://github.com/eric-wieser/type_templating/issues",
        "Source Code": "https://github.com/eric-wieser/type_templating",
    },

    python_requires='>=3.5',
)
