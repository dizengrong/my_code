from setuptools import setup, find_packages

__version__ = '0.1.1'

setup(
    name = 'bertrpc',
    license='MIT',
    version = __version__,
    description = 'BERT-RPC Library',
    author = 'Michael J. Russo',
    author_email = 'mjrusso@gmail.com',
    url = 'http://github.com/mjrusso/python-bertrpc',
    packages = ['bertrpc'],
    install_requires = ["erlastic", "bert"],
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
