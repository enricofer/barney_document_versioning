import os
from setuptools import find_packages, setup

import sys
if sys.version_info[0] < 3:
    print ("This package does not support Python 2.")
    sys.exit(1)

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='barney-version',
    version='0.1.11',
    packages=find_packages(),
    install_requires=[
        'Django==1.11.20',
        'webstack-django-jwt-auth==0.5.2',
        'django-markymark',
        'diff-match-patch',
        'django-cors-headers',
        'pypandoc',
        'Markdown',
    ],
    include_package_data=True,
    license='GNU General Public License v3 (GPLv3)',  # example license
    description='A Django app for easy/collaborative versioning of legal documents.',
    url='https://github.com/enricofer/simple_md_versioning',
    author='Enrico Ferreguti',
    author_email='enricofer@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',  # replace "X.Y" as appropriate
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
