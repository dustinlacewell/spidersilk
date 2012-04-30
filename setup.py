#!/usr/bin/env python

from setuptools import setup

setup(
    name='spidersilk',
    version='0.1',
    description="A declarative configuration library for twisted.web",
    url='http://github.com/dustinlacewell/spidersilk',

    packages=find_packages(),
    install_requires=[
        'Twisted==12.0.0',
    ],
)
