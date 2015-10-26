# Pyriscope

A simple Periscope video downloader for Python.

* Easily download any available Periscope stream by simply giving Pyriscope the URL.
* Pyriscope automatically downloads and stitches together Periscope video chunks.
* Optionally, Pyriscope converts the downloaded .ts file to a .mp4 file with optional rotation. (Requires ffmpeg)

Usage:
    `pyriscope <urls> [options]`

See `pyriscope --help` for further details.

### Version
1.2.5

### About

Author: Russell Harkanson <[@RussHarkanson]>

Pyriscope was influenced by [n3tman/periscope.tv], a Windows batch script for downloading Periscope videos.

Pyriscope is open source, with a [public repo][git-repo-url] on Github.

### Installation

```sh
$ pip install pyriscope
```

If Pyriscope is already installed, upgrade to the latest version with:

```sh
$ pip install pyriscope --upgrade
```

### Usage

```sh
$ pyriscope <urls> [options]
```

url accepted forms:

    https://www.periscope.tv/w/1LyxBeXmWObJN

    https://www.periscope.tv/w/aM1wNjE1ODAxMHwxcm14UGF2UkxOREtOGeN8ChyFlAXW4ihB_3NA9h3UysetWhz5G8WQdi7dsro=

    https://www.periscope.tv/Flad_Land/1zqJVmdaBvXGB

    http://www.perisearch.net/w/aM7_kzIzMjk1NTJ8MU1ZR05iWkFhUnZHd2_M8lSATtJLmbT0wvem7Ml6TTJgRS4_ReuSeQNGN73z


options:

    -h, --help              Show help. (This)

    -c, --convert           Convert download (.ts) to mp4. (Requires ffmpeg)

    -C, --clean             Convert, then clean up (delete) .ts file. (Requires ffmpeg)

    -r, --rotate            If convert, rotate converted video.

    -a, --agent             Turn on random user agent mocking. (Adds extra HTTP request)

    -n, --name <file>       Name the file (for single URL input only).

    -t <duration>           The duration (defined by ffmpeg) to record live streams.


`duration` is defined by [ffmpeg Time duration].


License
----

The MIT License (MIT)

Copyright (c) 2015 Russell Harkanson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

[//]: # (Ref links)

   [n3tman/periscope.tv]: <https://github.com/n3tman/periscope.tv>
   [git-repo-url]: <https://github.com/rharkanson/pyriscope>
   [@RussHarkanson]: <http://twitter.com/RussHarkanson>
   [ffmpeg]: <https://www.ffmpeg.org/>
   [ffmpeg Time duration]: <https://www.ffmpeg.org/ffmpeg-utils.html#time-duration-syntax>