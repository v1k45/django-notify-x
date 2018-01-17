# -*- encoding: utf-8 -*-
import os
from setuptools import setup, find_packages
import notify as app


install_requires = open('requirements.txt').read().splitlines()


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="django-notify-x",
    version=app.__version__,
    description='Notification sytem for Django',
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django notifications, notify, facebook like notifications',
    author='Vikas Yadav',
    author_email='v1k45x@gmail.com',
    url="https://github.com/v1k45/django-notify-x",
    packages=find_packages(),
    package_data={'notify': ['static/notify/*js',
                             'templates/*.html',
                             'templates/notifications/*.html',
                             'templates/notifications/includes/*.html',
                             'templates/notifications/includes/*.js']},
    include_package_data=True,
    install_requires=install_requires,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
    ]
)
