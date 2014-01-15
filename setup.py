#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['xbob.blitz', 'xbob.io', 'xbob.learn.activation']))
from xbob.blitz.extension import Extension
import xbob.io

import os
package_dir = os.path.dirname(os.path.realpath(__file__))
package_dir = os.path.join(package_dir, 'xbob', 'learn', 'linear', 'include')
include_dirs = [
    package_dir,
    xbob.blitz.get_include(),
    xbob.io.get_include(),
    xbob.learn.activation.get_include()
    ]

packages = ['bob-machine >= 1.3']
version = '2.0.0a0'

setup(

    name='xbob.learn.linear',
    version=version,
    description='Bindings for bob.machine\'s LinearMachine and Trainers',
    url='http://github.com/anjos/xbob.learn.linear',
    license='BSD',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
      'setuptools',
      'xbob.blitz',
      'xbob.io',
      'xbob.learn.activation',
    ],

    namespace_packages=[
      "xbob",
      "xbob.learn",
      ],

    ext_modules = [
      Extension("xbob.learn.linear._library",
        [
          "xbob/learn/linear/machine.cpp",
          "xbob/learn/linear/main.cpp",
          ],
        packages = packages,
        include_dirs = include_dirs,
        version = version,
        ),
      ],

    entry_points={
      'console_scripts': [
        ],
      },

    classifiers = [
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],

    )