# Pyriscope

A simple Periscope video downloader for Python.

* Easily download any available Periscope stream by simply giving pyriscope the URL.
* Pyriscope automatically downloads and stitches together Periscope chunks.
* Optionally, pyriscope converts the downloaded .ts file to a .mp4 file with optional rotation. (Requires ffmpeg)

Usage:
    `pyriscope <urls> [options]`

See `pyriscope --help` for further details.

### Version
1.1.4

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
$ python /path/to/pyriscope <urls> [options]
```

To enable conversion and rotation, [ffmpeg] is required.

### Development

* Multi-threaded download support for quicker download speeds.

License
----

MIT

[//]: # (Ref links)

   [n3tman/periscope.tv]: <https://github.com/n3tman/periscope.tv>
   [git-repo-url]: <https://github.com/rharkanson/pyriscope>
   [@RussHarkanson]: <http://twitter.com/RussHarkanson>
   [ffmpeg]: <https://www.ffmpeg.org/>
