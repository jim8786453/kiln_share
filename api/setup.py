#!/usr/bin/env python
import os
import platform

from setuptools import setup
from pip.req import parse_requirements

req_file = 'requirements.txt'
install_reqs = parse_requirements(req_file, session=False)
reqs = [str(ir.req) for ir in install_reqs]
del os.link

setup(
    author='Jim Kennedy',
    author_email='jim@kohlstudios.co.uk',
    description='Api for kilnshare.co.uk',
    install_requires=reqs,
    name='kiln_share',
    packages=['kiln_share'],
    version='0.0.1',
)
