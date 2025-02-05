#!/usr/bin/env python
from setuptools import setup

try:
    from testr.setup_helper import cmdclass
except ImportError:
    cmdclass = {}

setup(name='acispy',
      packages=['acispy'],
      use_scm_version=True,
      setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
      description='Python tools for ACIS Ops',
      author='John ZuHone',
      author_email='john.zuhone@cfa.harvard.edu',
      url='http://github.com/acisops/acispy',
      install_requires=["numpy>=1.12.1","requests","astropy"],
      classifiers=[
          'Intended Audience :: Science/Research',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3'
      ],
      include_package_data=True,
      tests_require=["pytest"],
      zip_safe=False,
      cmdclass=cmdclass,
      )
