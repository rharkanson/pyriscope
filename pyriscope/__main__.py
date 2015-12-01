"""
Copyright (c) 2015 Russell Harkanson

See the file LICENSE.txt for copying permission.
"""

import sys

if sys.version < '3':
    print("Error: Python 3+ required to run Pyriscope.")
    sys.exit(1)


from pyriscope import processor

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) == 1 and args[0] == "__magic__":
        args = input("Enter args now: ").strip(' ').split(' ')

    processor.process(args)

if __name__ == "__main__":
    main()
