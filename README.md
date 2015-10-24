# Pyriscope

A simple Periscope video downloader for Python.

* Easily download any available Periscope stream by simply giving pyriscope the URL.
* Pyriscope automatically downloads and stitches together Periscope chunks.
* Optionally, pyriscope converts the downloaded .ts file to a .mp4 file with optional rotation. (Requires ffmpeg)

Usage:
    `pyriscope <urls> [options]`

See `pyriscope --help` for further details.

### Version
1.2.0

### About

Author: Russell Harkanson <[@RussHarkanson]>

Pyriscope is influenced by [n3tman/periscope.tv], a Windows batch script also for downloading Periscope videos.

Pyriscope is open source, with a [public repo][git-repo-url] on Github.

### Installation

```sh
$ pip install pyriscope
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

    -a, --agent             Turn off user agent mocking. (Slightly quicker initial startup)

    -n, --name <file>       Name the file (for single URL input only).



License
----

MIT

[//]: # (Ref links)

   [n3tman/periscope.tv]: <https://github.com/n3tman/periscope.tv>
   [git-repo-url]: <https://github.com/rharkanson/pyriscope>
   [@RussHarkanson]: <http://twitter.com/RussHarkanson>
   [ffmpeg]: <https://www.ffmpeg.org/>
