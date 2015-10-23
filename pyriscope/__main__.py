import sys
import pyriscope


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) == 1 and args[0] == "__magic__":
        args = input("Enter args now: ").strip(' ').split(' ')

    pyriscope.process(args)

if __name__ == "__main__":
    main()
