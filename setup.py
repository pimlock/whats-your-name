from glob import glob
from os.path import splitext, basename

from setuptools import setup, find_packages

setup(
    name='whats-your-name',
    version='0.7.0',
    license='MIT License',
    packages=find_packages('code/src'),
    package_dir={'': 'code/src'},
    py_modules=[
        splitext(basename(path))[0] for path in glob('code/src/*.py')
    ],
    include_package_data=False,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    zip_safe=False,
    author='Piotr Mlocek',
    url='https://github.com/pimlock/whats-your-name'
)
