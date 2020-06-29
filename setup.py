"""Setup file"""
import hy

import os
import re
import codecs
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()
with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()

from importlib import reload

def find_version():
    here = os.path.abspath(os.path.dirname(__file__))
    there = os.path.join(here, 'minghu6', '__init__.py')

    version_file = codecs.open(there, 'r').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)

    else:
        raise RuntimeError("Unable to find version string.")


__version__ = find_version()

setup(
    name='minghu6',
    version=__version__,
    install_requires=REQUIRED,
    packages=find_packages(),
    package_data={
        'minghu6.algs': ['*.hy', '__pycache__/*'],
    },
    entry_points={
        'console_scripts': ['captcha=minghu6.tools.captcha.__main__:cli',
                            'ffmpeg-fix=minghu6.tools.ffmpeg_fix:cli',
                            # 'file_monitor=minghu6.tools.file_monitor:cli', #ONLY WINDOWS UPTONOW
                            'fileformat=minghu6.tools.fileformat:cli',
                            'launch=minghu6.tools.launch:cli',
                            'proxy-ip=minghu6.tools.proxy_ip:cli',
                            'yinyuetai=minghu6.tools.yinyuetai:cli',
                            'text-editor=minghu6.tools.text_editor:cli',
                            'youtube=minghu6.tools.youtube:cli',
                            'lc=minghu6.tools.lc:cli',
                            'add-pypath=minghu6.tools.add_pypath:cli',
                            'tieba=minghu6.tools.tieba:cli',
                            'head-py=minghu6.tools.head:cli',
                            'tail-py=minghu6.tools.tail:cli',
                            'text-py=minghu6.tools.text:cli',
                            'find_max-py=minghu6.tools.find_max:cli',
                            'find-py=minghu6.tools.find:cli',
                            'timeme=minghu6.tools.timeme:cli',
                            'daemon=minghu6.tools.daemon:cli',
                            'auto-resume=minghu6.tools.auto_resume:cli'
                           ],
    },
    include_package_data=True,
    license='BSD License',
    description='minghu6 Util Package',
    long_description_content_type="text/markdown",
    long_description=README,
    url='https://github.com/minghu6/minghu6_py',
    author='minghu6',
    author_email='a19678zy@163.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
