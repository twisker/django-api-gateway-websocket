# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


# Utility function to read the README.md file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README.md file and 2) it's easier to type in the README.md file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="django-api-gateway-websocket",
    version="0.0.1a",
    author='twister',
    description="a django app providing websocket functionality over aliyun api gateway",
    long_description=read('README.md'),
    packages=find_packages('.'),
    package_dir={'': '.'},
    package_data={
        '': [
            'templates/*.*',
            'templates/*/*.*',
            'templates/*/*/*.*',
            'templates/*/*/*/*.*',
            'templates/*/*/*/*/*.*',
            'templates/*/*/*/*/*/*.*',
            'templates/*/*/*/*/*/*/*.*',
            'templates/*/*/*/*/*/*/*/*.*',
            'templates/*/*/*/*/*/*/*/*/*.*',
            'static/*.*',
            'static/*/*.*',
            'static/*/*/*.*',
            'static/*/*/*/*.*',
            'static/*/*/*/*/*.*',
            'static/*/*/*/*/*/*.*',
            'static/*/*/*/*/*/*/*.*',
            'static/*/*/*/*/*/*/*/*.*',
            'static/*/*/*/*/*/*/*/*/*.*',
        ],
    },
    requires=[
        "Django",
        "requests",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Software Industry",
        "License :: Other/Proprietary License",
        "Natural Language :: Chinese (Simplified)",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
    ],
)
