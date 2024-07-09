# Library of Babel crawler

![](https://i.imgur.com/a0YUty2.png)
A native python program that uses the API of libraryofbabel.info and parses and stores interesting findings from the 
near infinite collection of books.

## Context about the Library of Babel and this repository
Based off a short story by Jorge Luis Borges, The Library of Babel imagines a library of every possible book that has
been written or will ever be written, and a librarian's account of working in this library.

libraryofbabel.info is a website that attempts to emulate the experience of browsing the near infinite possibilities of
the Library of Babel, and allows users to view selections of the library called hexes, which contain shelves of books.
Most of the books end up being random strings of characters however, so in practice (and in mathematical terms), it's
EXTREMELY unlikely you will find anything on your own.

This program attempts to automate the process of looking through millions of books of gibberish. It will first download
a book using an API call to directly download it, then using an english language word list, it will search
through each book and provide output via the console window and into a SQLite database. It primarily searches 
for words that are next to each other, while also keeping track of the largest word it found.

## Developer notes
I've been casually working on this for many years as a way to improve my own coding skills, to fill my fanciful need for
discovery, and to otherwise amuse myself by coding. I never intended the code to be public, but since others have shown
interest in using such a program, I have decided to make steps to get it out in the open. 

There will be frequent changes in the coming weeks/months as I work on getting this repository to be public facing, and 
to make it more user-friendly in general.

## Roadmap

0. ~~Code cleanup and refactoring~~
1. ~~Allow for easy running of scripts for non-technical users. This will likely include a way to store results that does 
not require MySQL.~~
2. ~~Better reporting in general, ideally with some fancy local website creation, or something to that effect.~~
3. More search options


# Program setup
1. Download and install Python 3.12.4
2. Ideally create a virtual environment with venv (this makes it so if you ever do other python work, required modules
stay only with this venv) and activate it
3. Download this codebase, navigate to it, and run `pip install -r requirements.txt`

# Getting started
0. For best results if using Windows, run in Powershell.
1. To run the program against a random single hex simply type `python runbabel.py -f`
2. To specify which hex to run against type `python runbabel.py specifiedhex -f`, Note: Hexes can only be alphanumeric
3. Throughout the run the results will be displayed in the console window, and also stored in a SQLite database called
babel.db located in the root directory of the program, this db can be accessed with any Sqllite workbench, such as
SQLitestudio: https://sqlitestudio.pl/

# Other options
Specific location start can with the flags --wall, --shelf and --volume or -w, -s and -v. For example to start at 
wall 3, shelf 2 and volume 4 of hex 'specifiedhex' by typing `python runbabel.py specifiedhex -f -w 3 -s 2 -v 4`

You can view a generated website with your findings by `python runbabel.py --results`, which will create a local
website viewable at `http://127.0.0.1:8050/`  An example of this output is shown below.

<img src="https://i.imgur.com/qqjtBbs.png" width="50%" height="50%">



