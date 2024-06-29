import sqlite3

db = sqlite3.connect("babel.db")
db.row_factory = sqlite3.Row
cur = db.cursor()

def handle_sql_hex(hex):
    cur.execute("CREATE TABLE IF NOT EXISTS hexes(hex_name)")
    result = cur.execute("SELECT ROWID FROM hexes WHERE hex_name = ?", (hex, ))
    hex_row_id = result.fetchall()
    if len(hex_row_id) == 0:
        print("Adding hex into hex table")
        cur.execute("INSERT INTO hexes (hex_name) VALUES(?)", (hex, ))
        db.commit()
        hex_id = cur.lastrowid
    elif len(hex_row_id) == 1:
        hex_id = hex_row_id[0]["rowid"]
        print("Found existing hex in table for hex: " + hex)
    else:
        raise Exception("Hex name exists in hexes table more than once!")

    return hex_id


def handle_sql_title(title, hex_id, hex, wall, shelf, volume):
    cur.execute("CREATE TABLE IF NOT EXISTS titles(rowid INTEGER PRIMARY KEY, title, hex, wall, shelf, volume)")
    result = cur.execute("SELECT * FROM titles WHERE title = ? AND hex = ? AND wall = ? AND shelf = ? AND volume = ?",
                   (title, hex_id, int(wall), int(shelf), int(volume)))
    titles = result.fetchall()
    if len(titles) == 0:
        cur.execute("INSERT INTO titles (title, hex, wall, shelf, volume) values (?, ?, ?, ?, ?)",
                    (title, hex_id, int(wall), int(shelf), int(volume)))
        db.commit()
        return cur.lastrowid
    elif len(titles) == 1:
        print(
            "Title already exists in db: " + "Title: " + title + " Hex: " + str(hex) + " Wall: " + str(
                wall) + " Shelf: " + str(shelf) + " Volume: " + str(volume))
        return titles[0]["rowid"]
    else:
        raise Exception("Title exists in hexes table more than once!")


def handle_sql_page(title_id, found_words):
    cur.execute("""CREATE TABLE IF NOT EXISTS page(rowid INTEGER PRIMARY KEY, title, page_number, num_consecutive_words,
                num_word_sets, words, largest_word)""")
    for page_text_info in found_words:
        result = cur.execute("SELECT * FROM page WHERE title = ? AND page_number = ?",
                             (title_id, int(page_text_info["Page number"])))
        page = result.fetchall()
        if len(page) == 0:
            cur.execute("""INSERT INTO page (title, page_number, num_consecutive_words, num_word_sets,
                            words, largest_word) values (?, ?, ?, ?, ?, ?)""",
                        (title_id,
                         int(page_text_info["Page number"]),
                         int(page_text_info["Consecutive count"]),
                         len(page_text_info["Consecutive word sets"]),
                         str(page_text_info["Consecutive word sets"]),
                         str(page_text_info["Largest word"]))
                        )
            db.commit()
            return True
        else:
            return False


def sql_largest_book_word(title_id, largest_word):
    result = cur.execute("SELECT * FROM page WHERE title = ? AND page_number = ?",
                         (title_id, int(largest_word["page"])))
    page = result.fetchall()
    if len(page) == 0:
        cur.execute("INSERT INTO page (title, page_number, largest_word) values (?, ?, ?)",
                    (title_id, int(largest_word["page"]), largest_word["word"]))
        db.commit()
    elif len(page) == 1:
        cur.execute("UPDATE page SET largest_word = ? where rowid = ?",
                    (largest_word["word"], page[0]["rowid"]))
        db.commit()


def significant_title_entry(word_string, title_id):
    cur.execute("CREATE TABLE IF NOT EXISTS significant_titles(rowid INTEGER PRIMARY KEY, words, title)")
    cur.execute("INSERT INTO significant_titles SET words = ?, title = ?",
                (word_string, title_id))
    db.commit()
