import argparse
import babel

parser = argparse.ArgumentParser()
parser.add_argument('hex', type=str,  nargs='*', default=None, help='hex name to search, will generate a random string if none is given')
parser.add_argument('-t', '--titles_only', help='search hexes only for titles', action='store_true')
parser.add_argument('-f', '--full', help='search full books for strings of text', action='store_true')

args = parser.parse_args()

if args.full:
    b = babel.Babel()
    if args.hex:
        b.search_hex(hex=args.hex[0])
    else:
        b.search_hex()

elif args.titles_only:
    print("Title search goes here")
