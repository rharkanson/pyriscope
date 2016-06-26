"""
Copyright (c) 2015 Russell Harkanson

See the file LICENSE.txt for copying permission.
"""

import sys
import os
import shutil
import string
import re
import json
import requests
from subprocess import PIPE, Popen
from datetime import datetime
from dateutil import tz
from queue import Queue
from threading import Thread


# Contants.
__author__ = 'Russell Harkanson'
VERSION = "1.2.7"
TERM_W = shutil.get_terminal_size((80, 20))[0]
STDOUT = "\r{:<" + str(TERM_W) + "}"
STDOUTNL = "\r{:<" + str(TERM_W) + "}\n"
PERISCOPE_GETBROADCAST = "https://api.periscope.tv/api/v2/getBroadcastPublic?{}={}"
PERISCOPE_GETACCESS = "https://api.periscope.tv/api/v2/getAccessPublic?{}={}"
ARGLIST_HELP = ('', '-h', '--h', '-help', '--help', 'h', 'help', '?', '-?', '--?')
ARGLIST_CONVERT = ('-c', '--convert')
ARGLIST_CLEAN = ('-C', '--clean')
ARGLIST_ROTATE = ('-r', '--rotate')
ARGLIST_AGENTMOCK = ('-a', '--agent')
ARGLIST_NAME = ('-n', '--name')
ARGLIST_TIME = ('-t')
DEFAULT_UA = "Mozilla\/5.0 (Windows NT 6.1; WOW64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/45.0.2454.101 Safari\/537.36"
DEFAULT_DL_THREADS = 6
FFMPEG_NOROT = "ffmpeg -y -v error -i \"{0}.ts\" -bsf:a aac_adtstoasc -codec copy \"{0}.mp4\""
FFMPEG_ROT ="ffmpeg -y -v error -i \"{0}.ts\" -bsf:a aac_adtstoasc -acodec copy -vf \"transpose=2\" -crf 30 \"{0}.mp4\""
FFMPEG_LIVE = "ffmpeg -y -v error -headers \"Referer:{}; User-Agent:{}\" -i \"{}\" -c copy{} \"{}.ts\""
URL_PATTERN = re.compile(r'(http://|https://|)(www.|)(periscope.tv|perisearch.net)/(w|\S+)/(\S+)')
REPLAY_URL = "https://replay.periscope.tv/{}/{}"
REPLAY_PATTERN = re.compile(r'https://replay.periscope.tv/(\S*)/(\S*)')


# Classes.
class Worker(Thread):
    def __init__(self, thread_pool):
        Thread.__init__(self)
        self.tasks = thread_pool.tasks
        self.tasks_info = thread_pool.tasks_info
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try: func(*args, **kargs)
            except Exception:
                print("\nError: Threadpool error.")
                sys.exit(1)

            self.tasks_info['num_tasks_complete'] += 1
            perc = int((self.tasks_info['num_tasks_complete']/self.tasks_info['num_tasks'])*100)
            sys.stdout.write(STDOUT.format("[{:>3}%] Downloading replay {}.ts.".format(perc, self.tasks_info['name'])))
            sys.stdout.flush()

            self.tasks.task_done()


class ThreadPool:
    def __init__(self, name, num_threads, num_tasks):
        self.tasks = Queue(num_threads)
        self.tasks_info = {
            'name': name,
            'num_tasks': num_tasks,
            'num_tasks_complete': 0
        }
        for _ in range(num_threads): Worker(self)

    def add_task(self, func, *args, **kwargs):
        self.tasks.put((func, args, kwargs))

    def wait_completion(self):
        self.tasks.join()


# Functions.
def show_help():
    if shutil.which("ffmpeg") is not None:
        ffmpeg_status = "FOUND! Live stream recording and conversion/rotation is available!"
    else:
        ffmpeg_status = "NOT FOUND! Live stream recording and conversion/rotation is NOT available."

    print("""version {}

Usage:
    pyriscope <urls> [options]

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

ffmpeg status:
    {}

About:
    Pyriscope is written by {} and distributed under the MIT license.
    See the file LICENSE.txt for copying permission.

    Pyriscope was influenced by n3tman/periscope.tv, a Windows batch script for downloading Periscope videos.

    Pyriscope is open source, with a public repo on Github.
        https://github.com/rharkanson/pyriscope
        """.format(VERSION, ffmpeg_status, __author__))
    sys.exit(0)


def dissect_url(url):
    match = re.search(URL_PATTERN, url)
    parts = {}

    try:
        parts['url'] = match.group(0)
        parts['website'] = match.group(3)
        parts['username'] = match.group(4)
        parts['token'] = match.group(5)

        if len(parts['token']) < 15:
            parts['broadcast_id'] = parts['token']
            parts['token'] = ""

    except:
        print("\nError: Invalid URL: {}".format(url))
        sys.exit(1)

    return parts


def dissect_replay_url(url):
    match = re.search(REPLAY_PATTERN, url)
    parts = {}

    try:
        parts['key'] = match.group(1)
        parts['file'] = match.group(2)

    except:
        print("\nError: Invalid Replay URL: {}".format(url))
        sys.exit(1)

    return parts


def get_mocked_user_agent():
    try:
        response = requests.get("http://api.useragent.io/")
        response = json.loads(response.text)
        return response['ua']
    except:
        try:
            response = requests.get("http://labs.wis.nu/ua/")
            response = json.loads(response.text)
            return response['ua']
        except:
            return DEFAULT_UA


def stdout(s):
    sys.stdout.write(STDOUT.format(s))
    sys.stdout.flush()


def stdoutnl(s):
    sys.stdout.write(STDOUTNL.format(s))
    sys.stdout.flush()


def sanitize(s):
    valid = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized = ''.join(char for char in s if char in valid)
    return sanitized


def download_chunk(url, headers, path):
    with open(path, 'wb') as handle:
        data = requests.get(url, stream=True, headers=headers)

        if not data.ok:
            print("\nError: Unable to download chunk.")
            sys.exit(1)
        for block in data.iter_content(4096):
            handle.write(block)


def process(args):
    # Make sure there are args, do a primary check for help.
    if len(args) == 0 or args[0] in ARGLIST_HELP:
        show_help()

    # Defaults arg flag settings.
    url_parts_list = []
    ffmpeg = True
    convert = False
    clean = False
    rotate = False
    agent_mocking = False
    name = ""
    live_duration = ""
    req_headers = {}

    # Check for ffmpeg.
    if shutil.which("ffmpeg") is None:
        ffmpeg = False

    # Read in args and set appropriate flags.
    cont = None
    for i in range(len(args)):
        if cont == ARGLIST_NAME:
            if args[i][0] in ('\'', '\"'):
                if args[i][-1:] == args[i][0]:
                    cont = None
                    name = args[i][1:-1]
                else:
                    cont = args[i][0]
                    name = args[i][1:]
            else:
                cont = None
                name = args[i]
            continue
        if cont in ('\'', '\"'):
            if args[i][-1:] == cont:
                cont = None
                name += " {}".format(args[i][:-1])
            else:
                name += " {}".format(args[i])
            continue
        if cont == ARGLIST_TIME:
            cont = None
            live_duration = args[i]

        if re.search(URL_PATTERN, args[i]) is not None:
            url_parts_list.append(dissect_url(args[i]))
        if args[i] in ARGLIST_HELP:
            show_help()
        if args[i] in ARGLIST_CONVERT:
            convert = True
        if args[i] in ARGLIST_CLEAN:
            convert = True
            clean = True
        if args[i] in ARGLIST_ROTATE:
            convert = True
            rotate = True
        if args[i] in ARGLIST_AGENTMOCK:
            agent_mocking = True
        if args[i] in ARGLIST_NAME:
            cont = ARGLIST_NAME
        if args[i] in ARGLIST_TIME:
            cont = ARGLIST_TIME


    # Check for URLs found.
    if len(url_parts_list) < 1:
        print("\nError: No valid URLs entered.")
        sys.exit(1)

    # Disable conversion/rotation if ffmpeg is not found.
    if convert and not ffmpeg:
        print("ffmpeg not found: Disabling conversion/rotation.")
        convert = False
        clean = False
        rotate = False

    # Set a mocked user agent.
    if agent_mocking:
        stdout("Getting mocked User-Agent.")
        req_headers['User-Agent'] = get_mocked_user_agent()
    else:
        req_headers['User-Agent'] = DEFAULT_UA


    url_count = 0
    for url_parts in url_parts_list:
        url_count += 1

        # Disable custom naming for multiple URLs.
        if len(url_parts_list) > 1:
            name = ""

        # Public Periscope API call to get information about the broadcast.
        if url_parts['token'] == "":
            req_url = PERISCOPE_GETBROADCAST.format("broadcast_id", url_parts['broadcast_id'])
        else:
            req_url = PERISCOPE_GETBROADCAST.format("token", url_parts['token'])

        stdout("Downloading broadcast information.")
        response = requests.get(req_url, headers=req_headers)
        broadcast_public = json.loads(response.text)

        if 'success' in broadcast_public and broadcast_public['success'] == False:
            print("\nError: Video expired/deleted/wasn't found: {}".format(url_parts['url']))
            continue

        # Loaded the correct JSON. Create file name.
        if name[-3:] == ".ts":
            name = name[:-3]
        if name[-4:] == ".mp4":
            name = name[:-4]
        if name == "":
            broadcast_start_time_end = broadcast_public['broadcast']['start'].rfind('.')
            timezone = broadcast_public['broadcast']['start'][broadcast_start_time_end:]
            timezone_start = timezone.rfind('-') if timezone.rfind('-') != -1 else timezone.rfind('+')
            timezone = timezone[timezone_start:].replace(':', '')
            to_zone = tz.tzlocal()
            broadcast_start_time = broadcast_public['broadcast']['start'][:broadcast_start_time_end]
            broadcast_start_time = "{}{}".format(broadcast_start_time, timezone)
            broadcast_start_time_dt = datetime.strptime(broadcast_start_time, '%Y-%m-%dT%H:%M:%S%z')
            broadcast_start_time_dt = broadcast_start_time_dt.astimezone(to_zone)
            broadcast_start_time = "{}-{:02d}-{:02d} {:02d}-{:02d}-{:02d}".format(
                broadcast_start_time_dt.year, broadcast_start_time_dt.month, broadcast_start_time_dt.day,
                broadcast_start_time_dt.hour, broadcast_start_time_dt.minute, broadcast_start_time_dt.second)
            name = "{} ({})".format(broadcast_public['broadcast']['username'], broadcast_start_time)

        name = sanitize(name)

        # Get ready to start capturing.
        if broadcast_public['broadcast']['state'] == 'RUNNING':
            # Cannot record live stream without ffmpeg.
            if not ffmpeg:
                print("\nError: Cannot record live stream without ffmpeg: {}".format(url_parts['url']))
                continue

            # The stream is live, start live capture.
            name = "{}.live".format(name)

            if url_parts['token'] == "":
                req_url = PERISCOPE_GETACCESS.format("broadcast_id", url_parts['broadcast_id'])
            else:
                req_url = PERISCOPE_GETACCESS.format("token", url_parts['token'])

            stdout("Downloading live stream information.")
            response = requests.get(req_url, headers=req_headers)
            access_public = json.loads(response.text)

            if 'success' in access_public and access_public['success'] == False:
                print("\nError: Video expired/deleted/wasn't found: {}".format(url_parts['url']))
                continue

            time_argument = ""
            if not live_duration == "":
                time_argument = " -t {}".format(live_duration)

            live_url = FFMPEG_LIVE.format(
                url_parts['url'],
                req_headers['User-Agent'],
                access_public['hls_url'],
                time_argument,
                name)

            # Start downloading live stream.
            stdout("Recording stream to {}.ts".format(name))

            Popen(live_url, shell=True, stdout=PIPE).stdout.read()

            stdoutnl("{}.ts Downloaded!".format(name))

            # Convert video to .mp4.
            if convert:
                stdout("Converting to {}.mp4".format(name))

                if rotate:
                    Popen(FFMPEG_ROT.format(name), shell=True, stdout=PIPE).stdout.read()
                else:
                    Popen(FFMPEG_NOROT.format(name), shell=True, stdout=PIPE).stdout.read()

                stdoutnl("Converted to {}.mp4!".format(name))

                if clean and os.path.exists("{}.ts".format(name)):
                    os.remove("{}.ts".format(name))
            continue

        else:
            if not broadcast_public['broadcast']['available_for_replay']:
                print("\nError: Replay unavailable: {}".format(url_parts['url']))
                continue

            # Broadcast replay is available.
            if url_parts['token'] == "":
                req_url = PERISCOPE_GETACCESS.format("broadcast_id", url_parts['broadcast_id'])
            else:
                req_url = PERISCOPE_GETACCESS.format("token", url_parts['token'])

            stdout("Downloading replay information.")
            response = requests.get(req_url, headers=req_headers)
            access_public = json.loads(response.text)

            if 'success' in access_public and access_public['success'] == False:
                print("\nError: Video expired/deleted/wasn't found: {}".format(url_parts['url']))
                continue

            base_url = access_public['replay_url']
            base_url_parts = dissect_replay_url(base_url)

            req_headers['Cookie'] = "{}={};{}={};{}={}".format(access_public['cookies'][0]['Name'],
                                                               access_public['cookies'][0]['Value'],
                                                               access_public['cookies'][1]['Name'],
                                                               access_public['cookies'][1]['Value'],
                                                               access_public['cookies'][2]['Name'],
                                                               access_public['cookies'][2]['Value'])
            req_headers['Host'] = "replay.periscope.tv"

            # Get the list of chunks to download.
            stdout("Downloading chunk list.")
            response = requests.get(access_public['replay_url'], headers=req_headers)
            chunks = response.text
            chunk_pattern = re.compile(r'chunk_\d+\.ts')

            download_list = []
            for chunk in re.findall(chunk_pattern, chunks):
                download_list.append(
                    {
                        'url': REPLAY_URL.format(base_url_parts['key'], chunk),
                        'file_name': chunk
                    }
                )

            # Download chunk .ts files and append them.
            pool = ThreadPool(name, DEFAULT_DL_THREADS, len(download_list))

            temp_dir_name = ".pyriscope.{}".format(name)
            if not os.path.exists(temp_dir_name):
                os.makedirs(temp_dir_name)

            stdout("Downloading replay {}.ts.".format(name))

            for chunk_info in download_list:
                temp_file_path = "{}/{}".format(temp_dir_name, chunk_info['file_name'])
                chunk_info['file_path'] = temp_file_path
                pool.add_task(download_chunk, chunk_info['url'], req_headers, temp_file_path)

            pool.wait_completion()

            if os.path.exists("{}.ts".format(name)):
                try:
                    os.remove("{}.ts".format(name))
                except:
                    stdoutnl("Failed to delete preexisting {}.ts.".format(name))

            with open("{}.ts".format(name), 'wb') as handle:
                for chunk_info in download_list:
                    with open(chunk_info['file_path'], 'rb') as ts_file:
                        handle.write(ts_file.read())

            if os.path.exists(temp_dir_name):
                try:
                    shutil.rmtree(temp_dir_name)
                except:
                    stdoutnl("Failed to delete temp folder: {}.".format(temp_dir_name))

            stdoutnl("{}.ts Downloaded!".format(name))

            # Convert video to .mp4.
            if convert:
                stdout("Converting to {}.mp4".format(name))

                if rotate:
                    Popen(FFMPEG_ROT.format(name), shell=True, stdout=PIPE).stdout.read()
                else:
                    Popen(FFMPEG_NOROT.format(name), shell=True, stdout=PIPE).stdout.read()

                stdoutnl("Converted to {}.mp4!".format(name))

                if clean and os.path.exists("{}.ts".format(name)):
                    try:
                        os.remove("{}.ts".format(name))
                    except:
                        stdout("Failed to delete {}.ts.".format(name))

    sys.exit(0)
