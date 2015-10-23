import sys
from pyriscope import process


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) == 1 and args[0] == "__magic__":
        args = input("Enter args now: ").strip(' ').split(' ')

    # process(args)
    print(sys.path)

if __name__ == "__main__":
    main()
