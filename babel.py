import urllib
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
from collections import Counter
from alive_progress import alive_bar
import storage
import generators
import bookstats


class Babel:

    def __init__(self):
        self.base_url = 'http://libraryofbabel.info/book.cgi?'
        self.hex = None
        self.wall = 1
        self.shelf = 1
        self.volume = 1  # max 32
        self.volume_string = self.convert_volume_to_string(self.volume)
        self.title = ""
        self.page = 1
        self.hex_complete = False
        self.word_list_longest_word_length = 0
        self.word_list = self.store_word_list('Data/words_alpha.txt')
        self.book_text = []
        self.largest_sequence = 0
        self.hex_id = None
        self.title_id = None

    def get_book_location(self):
        return self.hex + "-w" + str(self.wall) + "-s" + str(self.shelf) + "-v" + str(self.volume)

    def download_book(self, hex, wall, shelf):
        self.book_text = []
        self.volume_string = self.convert_volume_to_string(self.volume)
        book_title = self.get_wall_titles(hex, wall, shelf, self.volume)
        self.title = book_title
        if " " in book_title:
            book_title.replace(" ", "+")
        url = 'https://libraryofbabel.info/download.cgi?'
        params = dict(hex=self.hex, wall=self.wall, shelf=self.shelf,
                      volume=self.volume_string, page="", title=book_title)
        quoted_params = urlencode(params)
        full_url = url + quoted_params
        user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.104 Safari/537.36')
        headers = {'User-Agent':user_agent,}

        request = urllib.request.Request(full_url, None, headers)
        with alive_bar(title="Downloading next book...") as bar:
            try:
                response = urlopen(request).read()
            except HTTPError as e:
                print('HTTPError code: ', e.code)
                exit()
            except URLError as e:
                print('Reason: ', e.reason)
                exit()

            response = response.decode('ascii').split(';')
            response = response[0].replace("\n\n\nBook Location:" + self.hex + "-w" + str(self.wall)
                                           + "-s" + str(self.shelf) + "-v" + str(self.volume) + "\n", "")
            response = response.split("\n", 2)[2]
            bar()

        return response

    def search_shelf_for_words(self, hex, wall, shelf):
        while self.volume <= 32 and self.shelf == shelf and not self.hex_complete:
            self.parse_book_string(self.download_book(hex, wall, shelf))
            consecutive_words, largest_words = self.find_words()
            stats = self.get_max_consecutive_words_for_book(consecutive_words)
            print("Book Location: " + self.get_book_location(),
                  "\nBook Title: " + '\x1B[3m' + str(self.title) + '\x1B[0m',
                  "\nMax word sets on a single page: "
                  + str(stats.max_word_sets) + " (pg. " + str(stats.max_word_sets_page_num) + ")",
                  "| Maximum consecutive words on a page: "
                  + str(stats.max_consecutive_words) + " (pg." + str(stats.max_consecutive_words_page_num) + ")",
                  "| Longest consecutive word group: "
                  + str(stats.word_list) + " (pg." + str(stats.word_list_page_num) + ")")
            print("Largest words:")
            if len(largest_words) > 1:
                for word in largest_words:
                    print("pg." + str(word[0]) + ": " + str(word[1]), end=" | ")
            else:
                print("pg." + str(largest_words[0][0]) + ": " + str(largest_words[0][1]), end="")

            print("\n")
            self.calculate_next_book()

    def search_hex(self, hex=None, wall=None, shelf=None, volume=None):
        # Search a specific location for both titles and words
        storage.create_sql_tables()
        if not hex:
            hex = generators.generate_animal_hex()
        self.hex = hex
        self.hex_id = storage.handle_sql_hex(self.hex)
        if not wall and not shelf and not volume:
            self.reset_default_hex_values()
            print("Searching hex:", hex)
        else:  # Starting at different location
            if wall:
                self.wall = wall
            if shelf:
                self.shelf = shelf
            if volume:
                self.volume = volume
                self.volume_string = self.convert_volume_to_string(self.volume)

        while not self.hex_complete:
            self.search_shelf_for_words(self.hex, self.wall, self.shelf)

    def reset_default_hex_values(self):
        self.wall = 1
        self.shelf = 1
        self.volume = 1
        self.volume_string = self.convert_volume_to_string(self.volume)
        self.page = 1
        self.title = ""
        self.hex_complete = False

    def parse_book_string(self, book_string):
        book = book_string.replace('\n', '')
        current_page = 1
        while current_page <= 410:
            self.book_text.append(book[current_page * 3200 - 3200: current_page * 3200])
            current_page += 1

    def find_words(self):

        self.title_id = storage.handle_sql_title(self.title, self.hex_id, self.hex,
                                                 self.wall, self.shelf, self.volume)
        consecutive_words = []
        book_largest_word = []
        for page_number, page_text in enumerate(self.book_text, start=1):

            page_info = self.search_page_for_words(page_number, page_text, split_type="space")

            if page_info["Largest words"]:
                if page_info["Consecutive count"] > 1:
                    consecutive_words.append(page_info)
                    storage.handle_sql_consecutive_words(self.title_id, page_info)
                if len(page_info["Largest words"][0]) > 2:
                    storage.sql_largest_word_on_page(self.title_id, page_number, page_info["Largest words"])

                for word in page_info["Largest words"]:
                    if not book_largest_word:
                        book_largest_word.append((page_number, word))
                    elif len(book_largest_word[0][1]) == len(word):
                        book_largest_word.append((page_number, word))
                    elif len(book_largest_word[0][1]) < len(word):
                        book_largest_word.clear()
                        book_largest_word.append((page_number, word))
                    else:
                        break

        storage.sql_call_commit()
        return consecutive_words, book_largest_word

    def search_page_for_words(self, page_number, page_text, split_type="space"):
        # Lowest level function for searching for words on a single page, returns a dict of the page number,
        # how many words are together separated by split_type (consecutive count),
        # what the largest grouping of those words are (word sets), and the largest single word on the page

        consecutive_words_count = 0
        consecutive_words_text = []
        best_consecutive_words_count = 0
        best_consecutive_words_text = []
        largest_words = []

        if split_type == "space":
            split_page_text = page_text.split(" ")
        elif split_type == "comma":
            split_page_text = page_text.split(",")
        elif split_type == "period":
            split_page_text = page_text.split(".")

        for potential_word in split_page_text:
            potential_word = self.remove_starting_ending_punctuation(potential_word)
            if potential_word:
                if len(potential_word) <= self.word_list_longest_word_length:  # Don't test words that are too long
                    words_in_potential_word = self.words_in_string(potential_word)
                    if words_in_potential_word:
                        consecutive_words_count += 1
                        consecutive_words_text.append(potential_word)
                        if largest_words:
                            if len(potential_word) > len(largest_words[0]):
                                largest_words.clear()
                                largest_words.append(potential_word)
                            elif len(potential_word) == len(largest_words[0]):
                                largest_words.append(potential_word)
                        else:
                            largest_words.append(potential_word)

                    else:
                        if consecutive_words_count > 1:
                            if consecutive_words_count > best_consecutive_words_count:
                                best_consecutive_words_count = consecutive_words_count
                                best_consecutive_words_text = []
                                best_consecutive_words_text.append(consecutive_words_text)
                            elif consecutive_words_count == best_consecutive_words_count:
                                best_consecutive_words_text.append(consecutive_words_text)

                        consecutive_words_count = 0
                        consecutive_words_text = []

        page_text_info = {"Page number": page_number,
                          "Consecutive count": best_consecutive_words_count,
                          "Consecutive word sets": best_consecutive_words_text,
                          "Largest words": largest_words}

        return page_text_info


    def remove_starting_ending_punctuation(self, potential_word):
        while potential_word.startswith(('.', ',', ' ')):
            potential_word = potential_word[1:]
        while potential_word.endswith(('.', ',', ' ')):
            potential_word = potential_word.rstrip(potential_word[-1])

        return potential_word

    def print_link(self):
        return ("Opening Page: http://libraryofbabel.info/book.cgi?" + self.hex + "-w" + str(self.wall)
                + "-s" + str(self.shelf) + "-v" + str(self.volume) + ":" + str(self.page))

    def convert_volume_to_string(self, volume):
        if volume < 10:
            stringVolume = "0" + str(volume)
        else:
            stringVolume = str(volume)
        return stringVolume

    def store_word_list(self, location):
        word_list = []
        word_dict = {}
        with open(location) as inputfile:
            for line in inputfile:
                word_list.append(line.strip().lower())

            for word in word_list:
                if len(word) > self.word_list_longest_word_length:
                    self.word_list_longest_word_length = len(word)
                first_chars = word[:3]
                if first_chars in word_dict:
                    word_dict[first_chars].append(word)
                else:
                    word_dict[first_chars] = [word]

        return word_dict

    def words_in_string(self, a_string):
        # takes any string and compares it to the word list to see if there is a matching word
        a_string = a_string.strip()
        first_chars = a_string[:3]
        try:
            words_found = set(self.word_list[first_chars]).intersection(a_string.split())
        except:
            words_found = None

        return words_found

    def calculate_next_book(self):
        self.volume = int(self.volume)
        if self.volume == 32:
            if self.shelf == 5:
                if self.wall != 4:
                    self.wall += 1
                    self.shelf = 1
                    self.volume = 1
                    self.page = 1
                else:
                    self.hex_complete = True
            else:
                self.shelf += 1
                self.volume = 1
                self.page = 1
        elif self.volume > 32:
            raise Exception("self.volume is greater than 32, and cannot be more than 32")
        else:
            self.volume += 1
            self.page = 1

    def get_max_consecutive_words_for_book(self, found_words):
        book = bookstats.BookStats()
        for page in found_words:
            if page["Consecutive word sets"] == self.return_longest_string_list(book.word_list, page["Consecutive word sets"]):
                longest_word_set = book.word_list
                for word_set in page["Consecutive word sets"]:
                    if word_set == self.return_longest_string_list(word_set, longest_word_set):
                        longest_word_set = word_set
                        book.word_list_page_num = page["Page number"]
                book.word_list = longest_word_set
            if len(page["Consecutive word sets"]) > book.max_word_sets:
                book.max_word_sets = len(page["Consecutive word sets"])
                book.max_word_sets_page_num = page["Page number"]
            if int(page["Consecutive count"]) > book.max_consecutive_words:
                book.max_consecutive_words = page["Consecutive count"]
                book.max_consecutive_words_page_num = page["Page number"]

        return book

    def return_longest_string_list(self, list1, list2):
        largest_sublist1 = 0
        largest_sublist2 = 0
        for sub_list in list1:
            list1_len = self.list_string_length(sub_list)
            if list1_len > largest_sublist1:
                largest_sublist1 = list1_len
        for sub_list in list2:
            list2_len = self.list_string_length(sub_list)
            if list2_len > largest_sublist2:
                largest_sublist2 = list2_len
        return list1 if largest_sublist1 > largest_sublist2 else list2


    def list_string_length(self, given_list):
        string_length = 0
        for string in given_list:
            string_length += len(string)
        return string_length

    def get_wall_titles(self, hex, wall, shelf, volume=False):
        url = 'https://libraryofbabel.info/titler.cgi?'
        params = dict(hex=hex, wall=wall, shelf=shelf)
        quoted_params = urlencode(params)
        full_url = url + quoted_params
        user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.104 Safari/537.36')
        headers = {'User-Agent':user_agent,}

        request = urllib.request.Request(full_url, None, headers)
        response = urlopen(request).read()
        if not volume:
            return response.decode('ascii').split(';')
        if volume:
            return response.decode('ascii').split(';')[volume-1]