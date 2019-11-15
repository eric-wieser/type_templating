#!/usr/bin/env python
"""
C++-style type templating for Python
"""
from setuptools import setup, find_packages
import os

version_path = os.path.join('type_templating', '_version.py')
exec(open(version_path).read())


setup(
    name='type_templating',
    version=__version__,  # noqa: F821
    license='MIT',
    description=__doc__,
    long_description=__doc__,
    author='Eric Wieser',
    url='http://type_templating.readthedocs.io',
    packages=find_packages(),
    package_dir={'type_templating': 'type_templating'},

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    python_requires='>=3.5',
)
