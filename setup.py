"""
Copyright (c) 2015 Russell Harkanson

See the file LICENSE.txt for copying permission.
"""

from setuptools import setup

__author__ = 'Russell Harkanson'
VERSION = '1.2.3'

setup(name='pyriscope',
      version=VERSION,
      author=__author__,
      author_email='rharkanson@gmail.com',
      url='https://github.com/rharkanson/pyriscope',
      description='A simple Periscope video downloader for Python.',
      license='MIT',
      packages=['pyriscope'],
      package_data={'pyriscope': ['*.txt']},
      download_url='https://github.com/rharkanson/pyriscope/tarball/{}'.format(VERSION),
      keywords=['video', 'downloader', 'Periscope'],
      classifiers=[],
      install_requires=["requests", "wheel", "six", "python-dateutil"],
      entry_points={
          'console_scripts': [
              'pyriscope = pyriscope.__main__:main'
          ]
      },
      long_description="""
Easily download any available Periscope stream by simply giving Pyriscope the URL.

Pyriscope automatically downloads and stitches together Periscope video chunks.

Optionally, Pyriscope converts the downloaded .ts file to a .mp4 file with optional rotation. (Requires ffmpeg)

Usage:
    pyriscope <urls> [options]

See 'pyriscope --help' for further details.
        """)
