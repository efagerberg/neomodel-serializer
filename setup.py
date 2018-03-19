import sys
from setuptools import setup, find_packages

setup(
    name='neomodel-serializer',
    version='0.0.1.dev1',
    description='Serialize neomodels',
    long_description=open('README.rst').read(),
    author='Evan Fagerberg',
    author_email='adioevan@gmail.com',
    zip_safe=True,
    url='http://github.com/efagerberg/neomodel-serializer',
    license='MIT',
    packages=find_packages(exclude=('tests',)),
    keywords='neo4j neomodel',
    install_requires=['neomodel>=3.2.5', 'six'],
    setup_requires=['pytest-runner'] 
        if any(x in ('pytest', 'test') for x in sys.argv) else [],
    tests_require=['mock', 'pytest', 'pytest-cov', 'pytest-xdist'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Database",
    ])
