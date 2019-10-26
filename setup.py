import sys
from setuptools import setup, find_packages
from django_summernote import version, PROJECT


MODULE_NAME = 'django_summernote'
PACKAGE_DATA = list()
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
]

# mock is available as unittest.mock in Python 3.3 onwards.
TESTS_REQUIRE = ['mock'] if sys.version_info < (3, 3, 0) else [] \
    + ['django-dummy-plug']

setup(
    name=PROJECT,
    version=version,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    author='django-summernote contributors',
    maintainer='django-summernote maintainers',
    url='http://github.com/summernote/django-summernote',

    description='Summernote plugin for Django',
    classifiers=CLASSIFIERS,

    install_requires=['django'],
    test_suite='runtests.runtests',
    tests_require=TESTS_REQUIRE,
)
