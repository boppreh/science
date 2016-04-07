"""
Usage instructions:

- If you are installing: `python setup.py install`
- If you are developing: `python setup.py sdist bdist --format=zip bdist_wheel --universal`
"""

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    long_description = open('README.rst').read()

from setuptools import setup

setup(
    name='sciplot',
    version='0.6.1',
    author='BoppreH',
    author_email='boppreh@gmail.com',
    packages=['sciplot'],
    install_requires=['matplotlib']
    url='https://github.com/boppreh/sciplot',
    license='MIT',
    description='Pythonic data visualization tool based on matplotlib',
    keywords = 'science graph plot matplotlib visualization',
    long_description=long_description,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Visualization',
        'Intended Audience :: Science/Research',
    ],
)
