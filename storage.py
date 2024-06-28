import pymysql.cursors

db= pymysql.connect(host="localhost",user="root",passwd="password",db="babel")
c = db.cursor(pymysql.cursors.DictCursor)


def handle_mysql_hex(hex):
    c.execute("""select id
                from hexes
                where hex_name = %s""", [hex])
    result = c.fetchall()
    if c.rowcount == 0:
        print("Adding hex into hex table")
        c.execute("""insert into hexes (hex_name) values (%s)""", [hex])
        db.commit()
        hex_id = c.lastrowid
    elif c.rowcount == 1:
        hex_id = result[0]["id"]
        print("Found existing hex in table for hex: " + hex)
    else:
        raise Exception("Hex name exists in hexes table more than once!")

    return hex_id


def handle_mysql_title(title, hex_id, hex, wall, shelf, volume):
    c.execute("""select * from titles
                where title= %s and hex= %s and wall= %s and shelf=% s and volume= %s""",
              [title, hex_id, int(wall), int(shelf), int(volume)])
    result = c.fetchall()
    if c.rowcount == 0:
        c.execute("""insert into titles (title, hex, wall, shelf, volume) values (%s, %s, %s, %s, %s)""",
                  [title, hex_id, int(wall), int(shelf), int(volume)])
        db.commit()
        return c.lastrowid
    elif c.rowcount == 1:
        print(
            "Title already exists in db: " + "Title: " + title + " Hex: " + str(hex) + " Wall: " + str(
                wall) + " Shelf: " + str(shelf) + " Volume: " + str(volume))
        return result[0]["id"]
    else:
        raise Exception("Title exists in hexes table more than once!")


def handle_mysql_page(title_id, found_words):
    for page_text_info in found_words:
        c.execute("""select * from page
                    where title= %s and page_number= %s""",
                  [title_id, int(page_text_info["Page number"])])
        result = c.fetchall()
        if c.rowcount == 0:
            c.execute("""insert into page (title, page_number, num_consecutive_words, num_word_sets,
                            words, largest_word) values (%s, %s, %s, %s, %s, %s)""",
                      [title_id,
                       int(page_text_info["Page number"]),
                       int(page_text_info["Consecutive count"]),
                       len(page_text_info["Consecutive word sets"]),
                       str(page_text_info["Consecutive word sets"]),
                       str(page_text_info["Largest word"])]
                      )
            db.commit()
            return
        else:
            return False


def mysql_largest_book_word(title_id, largest_word):
    c.execute("""select * from page
                where title= %s and page_number= %s""",
              [title_id, int(largest_word["page"])])
    result = c.fetchall()
    if c.rowcount == 0:
        c.execute("""insert into page (title, page_number, largest_word) values (%s, %s, %s)""",
                  [title_id, int(largest_word["page"]), largest_word["word"]])
        db.commit()
    elif c.rowcount == 1:
        c.execute("""update page set largest_word= %s where id= %s""",
                  [largest_word["word"], result[0]["id"]])
        db.commit()


def significant_title_entry(word_string, title_id):
    c.execute("""insert into significant_titles set words = %s, title = %s""",
              [word_string, title_id])
    db.commit()
