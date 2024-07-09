import sqlite3

db = sqlite3.connect("babel.db")
db.row_factory = sqlite3.Row
cur = db.cursor()


def create_sql_tables():
    cur.execute("CREATE TABLE IF NOT EXISTS hexes(rowid INTEGER PRIMARY KEY, hex_name)")
    cur.execute("CREATE TABLE IF NOT EXISTS titles(rowid INTEGER PRIMARY KEY, title, hex, wall, shelf, volume)")
    cur.execute("""CREATE TABLE IF NOT EXISTS consecutive_words(rowid INTEGER PRIMARY KEY, title_id, page_num,
                    num_consecutive_words, num_word_sets, words)""")
    cur.execute("CREATE TABLE IF NOT EXISTS page_words(rowid INTEGER PRIMARY KEY, title_id, page_num, length, word)")
    cur.execute("CREATE TABLE IF NOT EXISTS significant_titles(rowid INTEGER PRIMARY KEY, words, title)")
    db.commit()

def handle_sql_hex(hex):
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

def handle_sql_consecutive_words(title_id, page_info):
    result = cur.execute("SELECT * FROM consecutive_words WHERE title_id = ? and page_num = ?",
                         (title_id, int(page_info["Page number"])))
    page = result.fetchall()
    if len(page) == 0:
        cur.execute("""INSERT INTO consecutive_words (title_id, page_num, num_consecutive_words, num_word_sets,
                        words) values (?, ?, ?, ?, ?)""",
                    (title_id,
                     int(page_info["Page number"]),
                     int(page_info["Consecutive count"]),
                     len(page_info["Consecutive word sets"]),
                     str(page_info["Consecutive word sets"]))
                    )

def sql_largest_word_on_page(title_id, page_num, largest_words):
    result = cur.execute("SELECT * FROM page_words WHERE title_id = ? and page_num = ?",
                         (title_id, page_num))
    page = result.fetchall()
    if len(page) == 0:
        if len(largest_words) > 0:
            for word in largest_words:
                cur.execute("INSERT INTO page_words (title_id, page_num, length, word) values (?, ?, ?, ?)",
                            (title_id, page_num, len(word), word))


def sql_call_commit():
    db.commit()

def significant_title_entry(word_string, title_id):
    cur.execute("INSERT INTO significant_titles SET words = ?, title = ?",
                (word_string, title_id))
    db.commit()
