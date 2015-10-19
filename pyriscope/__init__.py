__author__ = 'Russell Harkanson'

import sys

if __name__ in ("__main__", "pyriscope"):
    import pyriscope.pyriscope

    sys.argv.pop(0)
    if len(sys.argv) == 1 and sys.argv[0] == "__magic__":
        pyriscope.main(input("Enter args now: ").strip(' ').split(' '))
    else:
        pyriscope.main(sys.argv)
else:
    from pyriscope import pyriscope
