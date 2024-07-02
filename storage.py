import sqlite3

db = sqlite3.connect("babel.db")
db.row_factory = sqlite3.Row
cur = db.cursor()


def handle_sql_hex(hex):
    cur.execute("CREATE TABLE IF NOT EXISTS hexes(hex_name)")
    result = cur.execute("SELECT ROWID FROM hexes WHERE hex_name = ?", (hex, ))
    hex_row_id = result.fetchall()
    if len(hex_row_id) == 0:
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


def handle_sql_page(title_id, page_number):
    cur.execute("""CREATE TABLE IF NOT EXISTS pages(rowid INTEGER PRIMARY KEY, title_id, page_number)""")
    result = cur.execute("SELECT * FROM pages WHERE title_id = ? and page_number = ?",
                         (title_id, page_number))
    page = result.fetchall()
    if len(page) == 0:
        cur.execute("INSERT INTO pages (title_id, page_number) values (?, ?)", (title_id, page_number))
        db.commit()
        return cur.lastrowid
    elif len(page) == 1:
        return page[0]["rowid"]
    else:
        raise Exception("Page exists in pages table more than once!")


def handle_sql_consecutive_words(page_id, page_info):
    cur.execute("""CREATE TABLE IF NOT EXISTS consecutive_words(rowid INTEGER PRIMARY KEY, page_id,
                num_consecutive_words, num_word_sets, words)""")
    result = cur.execute("SELECT * FROM consecutive_words WHERE page_id = ?", (page_id, ))
    page = result.fetchall()
    if len(page) == 0:
        cur.execute("""INSERT INTO consecutive_words (page_id, num_consecutive_words, num_word_sets,
                        words) values (?, ?, ?, ?)""",
                    (page_id,
                     int(page_info["Consecutive count"]),
                     len(page_info["Consecutive word sets"]),
                     str(page_info["Consecutive word sets"]))
                    )
        db.commit()
        return True
    else:
        return False

def sql_largest_word_on_page(page_id, largest_words):
    cur.execute("CREATE TABLE IF NOT EXISTS page_words(rowid INTEGER PRIMARY KEY, page_id, length, word)")
    result = cur.execute("SELECT * FROM page_words WHERE page_id = ?", (page_id, ))
    page = result.fetchall()
    if len(page) == 0:
        if len(largest_words) > 0:
            for word in largest_words:
                cur.execute("INSERT INTO page_words (page_id, length, word) values (?, ?, ?)",
                            (page_id, len(word), word))
                db.commit()

def significant_title_entry(word_string, title_id):
    cur.execute("CREATE TABLE IF NOT EXISTS significant_titles(rowid INTEGER PRIMARY KEY, words, title)")
    cur.execute("INSERT INTO significant_titles SET words = ?, title = ?",
                (word_string, title_id))
    db.commit()
