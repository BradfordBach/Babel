import argparse
import babel

parser = argparse.ArgumentParser()
parser.add_argument('hex', type=str,  nargs='*', default=None, help='hex name to search, will generate a random string if none is given')
parser.add_argument('-f', '--full', help='search full books for strings of text', action='store_true')

args = parser.parse_args()

if args.full:
    b = babel.Babel()
    if args.hex:
        if args.hex[0].isalnum():  # make sure hex name is only alphanumeric
            hex_name = args.hex[0].lower()
            b.search_hex(hex=hex_name)
        else:
            print("Hex name can only include numbers and letters with no special characters or spaces")
            exit()
    else:
        b.search_hex()
