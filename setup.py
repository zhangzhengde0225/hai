#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree
from unicodedata import name

from setuptools import find_packages, setup, Command


NAME = 'hepai'
DESCRIPTION = 'High energy physics Artificial Intelligence platform, HAI.'
URL = 'https://github.com/hepaihub/hepai'
EMAIL = 'zdzhang@ihep.ac.cn; xiongdb@ihep.ac.cn'
AUTHOR = 'Zhengde Zhang, Dongbo Xiong'
REQUIRES_PYTHON = '>=3.10.0'

with open(f'hai/version.py') as f:
    data = f.readlines()
    for line in data:
        if '__version__' in line:
            VERSION = line.split('=')[-1].strip().replace("'", '')
            break
    assert VERSION is not None, 'version is not found'
# VERSION = eval(data[0].split('=')[-1].strip())
print(f'Installing {NAME}, version: {VERSION}')


def read_requirements(filename='requirements.txt'):
    """读取 requirements 文件并过滤掉注释和空行"""
    requirements = []
    try:
        with open(filename) as f:
            for line in f:
                line = line.strip()
                # 跳过空行、注释行和分组标记行
                if line and not line.startswith('#') and not line.startswith('###'):
                    requirements.append(line)
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        requirements = []
    return requirements

def read_full_requirements():
    """读取完整的 requirements-full.txt 文件"""
    return read_requirements('requirements-full.txt')

# 基础依赖 - 从 requirements.txt 读取
REQUIRED = read_requirements()

# 完整依赖配置
EXTRAS = {
    'full': read_full_requirements(),
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine …')
        try:
            import twine  # 需要用twine上传，但twine不一定安装，如果没装报错
        except:
            raise NameError(
                f'You need twine to upload the package to pypi.\n'
                f'           Install twine with "pip install twine" or switch a environment with twine.')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
        ),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    entry_points={
         'console_scripts': ['hai = hai.uaii.cli.cli_main:run'],
    },

    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
