from __future__ import print_function

import os
import sys

from setuptools import setup, find_packages
from surveys import __version__

# Just run pytest and pass any additional args
if sys.argv[:2] == ["setup.py", "test"]:
    os.system('pytest %s' % " ".join(sys.argv[2:]))
    sys.exit()

setup(
    name='Mezzanine Surveys',
    version=__version__,
    description='Survey App for Mezzanine CMS',
    author='Ed Rivas',
    author_email='e@jerivas.com',
    url='https://github.com/jerivas/mezzanine-surveys',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    tests_require=[
        'pytest-django>=3.1,<3.2',
        'django-dynamic-fixture>=2.0,<2.1',
        'flake8>=3.5,<3.6',
    ],
    install_requires=[
        'mezzy==2.2.0',
    ]
)
