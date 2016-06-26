#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='push',
    version='0.0.1',
    description='Utility to push tar.gz docker images to v2 registry',
    author='Matej Cotman',
    author_email='cotman.matej@gmail.com',
    url='https://github.com/matejc/push',
    install_requires=['requests>=2.9.1'],
    packages=['push'],
    entry_points={
        'console_scripts': [
            'push=push.cli:main',
        ],
    }
)
