import argparse
import babel
import reporting.dash_output as output

parser = argparse.ArgumentParser()
parser.add_argument('hex', type=str,  nargs='*', default=None, help='hex name to search, will generate a random string if none is given')
parser.add_argument('-f', '--full', help='search full books for strings of text', action='store_true')
parser.add_argument('-w', '--wall', type=int)
parser.add_argument('-s', '--shelf', type=int)
parser.add_argument('-v', '--volume', type=int)
parser.add_argument('-r', '--results', help='Display results webpage', action='store_true')
args = parser.parse_args()

if args.full:
    b = babel.Babel()
    if args.hex:
        if args.hex[0].isalnum():  # make sure hex name is only alphanumeric
            hex_name = args.hex[0].lower()
            if args.wall and args.shelf and args.volume:
                b.search_hex(hex=hex_name, wall=args.wall, shelf=args.shelf, volume=args.volume)
            else:
                b.search_hex(hex=hex_name)
        else:
            print("Hex name can only include numbers and letters with no special characters or spaces")
            exit()
    else:
        b.search_hex()

elif args.results:
    output.run_sql_with_query()
