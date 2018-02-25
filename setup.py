from setuptools import setup, find_packages
from surveys import __version__

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
    install_requires=[
        'django-wkhtmltopdf==3.1.0',
    ]
)
