# Library of Babel crawler

A native python program that uses the API of libraryofbabel.info and parses and stores interesting findings from the 
near infinate collection of books.

## Context about the Library of Babel and this repository
Based off a short story by Jorge Luis Borges, The Library of Babel imagines a library of every possible book that has
been written or will ever be written, and a librarian's account of working in this library.

libraryofbabel.info is a website that attempts to emulate the experience of browsing the near infinite possibilities of
the Library of Babel, and allows users to view selections of the library called hexes, which contain shelves of books.
Most of the books end up being random strings of characters however, so in practice (and in mathematical terms), it's
EXTREMELY unlikely you will find anything on your own.

This program attempts to automate the process of looking through millions of books of gibberish. It will first download
a book using an API call to directly download it, then using an english language word list, it will search
through hexes and provide output via the console window as well as into a MySQL database. It primarily searches 
for words that are next to each other, while also keeping track of the largest word it found.

## Developer notes:
I've been casually working on this for many years as a way to improve my own coding skills, to fill my fanciful need for
discovery, and to otherwise amuse myself by coding. I never intended the code to be public, but since others have shown
interest in using such a program, I have decided to make steps to get it out in the open. 

There will be frequent changes in the coming weeks/months as I work on getting this repository to be public facing, and 
to make it more user-friendly in general. As such, instructions to run this program will be forthcoming, ~~since as of now
it requires setting up a MySQL database to run.~~

## Roadmap

0. Code cleanup and refactoring
1. Allow for easy running of scripts for non-technical users. ~~This will likely include a way to store results that does 
not require MySQL.~~
2. Better reporting in general, ideally with some fancy local website creation, or something to that effect.
3. More search options



