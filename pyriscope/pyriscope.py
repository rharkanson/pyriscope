__author__ = 'Russell Harkanson'

import sys
import os
import re
from subprocess import PIPE, Popen
import json
import requests
from datetime import datetime

# Contants.
STDOUT = "\r{:<60}"
STDOUTNL = "\r{:<60}\n"
PERISCOPE_GETBROADCAST = "https://api.periscope.tv/api/v2/getBroadcastPublic?{}={}"
PERISCOPE_GETACCESS = "https://api.periscope.tv/api/v2/getAccessPublic?{}={}"
ARGLIST_HELP = ('', '-h', '--h', '-help', '--help', 'h', 'help', '?', '-?', '--?')
ARGLIST_CONVERT = ('-c', '--convert')
ARGLIST_CLEAN = ('-C', '--clean')
ARGLIST_ROTATE = ('-r', '--rotate')
ARGLIST_AGENTMOCK = ('-a', '--agent')
ARGLIST_NAME = ('-n', '--name')
FFMPEG_NOROT = "ffmpeg -y -v error -i \"{0}.ts\" -bsf:a aac_adtstoasc -codec copy \"{0}.mp4\""
FFMPEG_ROT = "ffmpeg -y -v error -i \"{0}.ts\" -bsf:a aac_adtstoasc -acodec copy -vf \"transpose=2\" -crf 30 \"{0}.mp4\""
FFMPEG_LIVE = "ffmpeg -y -v error -headers \"Referer:{}; User-Agent:{}\" -i \"{}\" -c copy \"{}.ts\""
URL_PATTERN = re.compile(r'(http:\/\/|https:\/\/|)(www.|)(periscope.tv|perisearch.net)\/(w|\S+)\/(\S+)')


def show_help():
    print("""
version 1.1.2

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
    -a, --agent             Turn off user agent mocking. (Slightly quicker initial startup)
    -n, --name <file>       Name the file (for single URL input only).

About:
    Pyriscope is influenced by n3tman/periscope.tv, a Windows batch script also for downloading Periscope videos.

    Pyriscope is open source, with a public repo on Github.
        https://github.com/rharkanson/pyriscope

    """)
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
            return "Mozilla\/5.0 (X11; U; Linux i686; de; rv:1.9.0.18) Gecko\/2010020400 SUSE\/3.0.18-0.1.1 Firefox\/3.0.18"


def main(args):
    # Make sure there are args, do a primary check for help.
    if len(args) == 0 or args[0] in ARGLIST_HELP:
        show_help()

    # Defaults arg flag settings.
    url_parts_list = []
    convert = False
    clean = False
    rotate = False
    agent_mocking = True
    name = ""
    req_headers = {}

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
            rotate = True
        if args[i] in ARGLIST_AGENTMOCK:
            agent_mocking = False
        if args[i] in ARGLIST_NAME:
            cont = ARGLIST_NAME

    # Set a mocked user agent.
    if agent_mocking:
        sys.stdout.write(STDOUT.format("Getting mocked User-Agent."))
        sys.stdout.flush()
        req_headers['User-Agent'] = get_mocked_user_agent()


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

        sys.stdout.write(STDOUT.format("Downloading broadcast information."))
        sys.stdout.flush()
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
            broadcast_start_time = broadcast_public['broadcast']['start'].rfind('.')
            broadcast_start_time = broadcast_public['broadcast']['start'][:broadcast_start_time]
            broadcast_start_time = datetime.strptime(broadcast_start_time, '%Y-%m-%dT%H:%M:%S')
            broadcast_start_time = "{}-{}-{} {}-{}-{}".format(broadcast_start_time.year, broadcast_start_time.month,
                                                              broadcast_start_time.day, broadcast_start_time.hour,
                                                              broadcast_start_time.minute, broadcast_start_time.second)
            name = "{} ({})".format(broadcast_public['broadcast']['username'], broadcast_start_time)


        # Get ready to start capturing.
        if broadcast_public['broadcast']['state'] == 'RUNNING':
            # The stream is live, start live capture.
            name = "{}.live".format(name)

            if url_parts['token'] == "":
                req_url = PERISCOPE_GETACCESS.format("broadcast_id", url_parts['broadcast_id'])
            else:
                req_url = PERISCOPE_GETACCESS.format("token", url_parts['token'])

            sys.stdout.write(STDOUT.format("Downloading live stream information."))
            sys.stdout.flush()
            response = requests.get(req_url, headers=req_headers)
            access_public = json.loads(response.text)

            if 'success' in access_public and access_public['success'] == False:
                print("\nError: Video expired/deleted/wasn't found: {}".format(url_parts['url']))
                continue

            live_url = FFMPEG_LIVE.format(url_parts['url'], req_headers['User-Agent'], access_public['hls_url'], name)

            # Start downloading live stream.
            sys.stdout.write(STDOUT.format("Recording stream to {}.ts".format(name)))
            sys.stdout.flush()

            Popen(live_url, shell=True, stdout=PIPE).stdout.read()

            sys.stdout.write(STDOUTNL.format("{}.ts Downloaded!".format(name)))
            sys.stdout.flush()

            # Convert video to .mp4.
            if convert:
                sys.stdout.write(STDOUT.format("Converting to {}.mp4".format(name)))
                sys.stdout.flush()

                if rotate:
                    Popen(FFMPEG_ROT.format(name), shell=True, stdout=PIPE).stdout.read()
                else:
                    Popen(FFMPEG_NOROT.format(name), shell=True, stdout=PIPE).stdout.read()

                sys.stdout.write(STDOUTNL.format("Converted to {}.mp4!".format(name)))
                sys.stdout.flush()

                if clean:
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

            sys.stdout.write(STDOUT.format("Downloading replay information."))
            sys.stdout.flush()
            response = requests.get(req_url, headers=req_headers)
            access_public = json.loads(response.text)

            if 'success' in access_public and access_public['success'] == False:
                print("\nError: Video expired/deleted/wasn't found: {}".format(url_parts['url']))
                continue

            base_url = access_public['replay_url'][:-14]

            req_headers['Cookie'] = "{}={};{}={};{}={}".format(access_public['cookies'][0]['Name'],
                                                               access_public['cookies'][0]['Value'],
                                                               access_public['cookies'][1]['Name'],
                                                               access_public['cookies'][1]['Value'],
                                                               access_public['cookies'][2]['Name'],
                                                               access_public['cookies'][2]['Value'])
            req_headers['Host'] = "replay.periscope.tv"

            # Get the list of chunks to download.
            sys.stdout.write(STDOUT.format("Downloading chunk list."))
            sys.stdout.flush()
            response = requests.get(access_public['replay_url'], headers=req_headers)
            chunks = response.text
            chunk_pattern = re.compile(r'chunk_\d+\.ts')

            download_list = []
            for chunk in re.findall(chunk_pattern, chunks):
                download_list.append("{}/{}".format(base_url, chunk))

            # Download chunk .ts files and appened them.
            downloaded = True
            cnt = 0
            with open("{}.ts".format(name), 'wb') as handle:
                for chunk_url in download_list:
                    perc = int((cnt/len(download_list))*100)
                    sys.stdout.write(STDOUT.format("[{:>3}%] Downloading replay {}.ts.".format(perc, name)))
                    sys.stdout.flush()

                    data = requests.get(chunk_url, stream=True, headers=req_headers)

                    if not data.ok:
                        print("\nError: Unable to download chunk: {}".format(url_parts['url']))
                        downloaded = False
                        break
                    for block in data.iter_content(4096):
                        handle.write(block)
                    cnt += 1

            if downloaded:
                sys.stdout.write(STDOUTNL.format("{}.ts Downloaded!".format(name)))
                sys.stdout.flush()

                # Convert video to .mp4.
                if convert:
                    sys.stdout.write(STDOUT.format("Converting to {}.mp4".format(name)))
                    sys.stdout.flush()

                    if rotate:
                        Popen(FFMPEG_ROT.format(name), shell=True, stdout=PIPE).stdout.read()
                    else:
                        Popen(FFMPEG_NOROT.format(name), shell=True, stdout=PIPE).stdout.read()

                    sys.stdout.write(STDOUTNL.format("Converted to {}.mp4!".format(name)))
                    sys.stdout.flush()

                    if clean:
                        os.remove("{}.ts".format(name))

# Entry point.
if __name__ in ("__main__", "pyriscope"):
    sys.argv.pop(0)
    if len(sys.argv) == 1 and sys.argv[0] == "__magic__":
        main(input("Enter args now: ").strip(' ').split(' '))
    else:
        main(sys.argv)
else:
    print("Must be the first module ran.")
    print("python {} <url> [options]".format(os.path.dirname(__file__)))
    sys.exit(0)
