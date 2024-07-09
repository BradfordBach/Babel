from dash import Dash, html, dash_table, dcc
import pandas as pd
import plotly.express as px
import sqlite3


def run_sql_with_query():
    conn = sqlite3.connect('babel.db')
    sql = {"large_words": """select p.word, t.title, h.hex_name, p.page_num,
                        "https://libraryofbabel.info/book.cgi?" || h.hex_name || "-w" || t.wall || "-s" || t.shelf || "-v" 
                        || printf('%02d', t.volume) || ":" || p.page_num as URL from page_words as p
                        join titles as t on p.title_id=t.rowid
                        join hexes as h on t.hex=h.rowid
                        where p.length = (SELECT max(length) FROM page_words)""",
               "totals": """select count(title) as Total_Books, count(title) * 410 as Total_Pages from titles""",
               "full_hex": """select count(*) as Full_Hexes
                        from (select count(*) from hexes as h
                        join titles as t on h.rowid = t.hex
                        group by t.hex
                        having count(*) >= 640)""",
               "full_wall": """select count(*) as Full_Walls
                        from (select count(*) from titles
                        group by hex, wall
                        having count(*) >= 160)""",
               "full_shelf": """select count(*) as Full_Shelves
                        from (select count(*) from titles
                        group by hex, wall, shelf
                        having count(*) >= 32)""",
               "total_words": """select count(*) as num_words from page_words where length >= 3""",
               "longest_word": """select length from page_words
                        where length = (SELECT max(length) FROM page_words)
                        group by length""",
               "most_consec_words": """select num_consecutive_words as amount from consecutive_words as c
                        where amount = (SELECT max(num_consecutive_words) from consecutive_words)
                        group by amount;""",
               "hex_completion": """select count(*) as Books_Searched, h.hex_name from hexes as h
                        join titles as t on h.rowid = t.hex
                        group by t.hex
                        order by Books_Searched desc;""",
               "words_markup": """ select "[" || p.word || "](" || "https://libraryofbabel.info/book.cgi?" || h.hex_name 
                            || "-w" || t.wall || "-s" || t.shelf || "-v" || printf('%02d', t.volume) || ":" 
                            || p.page_num || ")" as word_markup, t.title, h.hex_name, p.page_num
                            from page_words as p
                            join titles as t on p.title_id=t.rowid
                            join hexes as h on t.hex=h.rowid
                            where p.length = ?"""}

    totals = pd.read_sql_query(sql["totals"], conn).to_dict('records')[0]
    total_words = pd.read_sql_query(sql["total_words"], conn).to_dict('records')
    total_words = f"{total_words[0]["num_words"]:,}"
    longest_word = pd.read_sql_query(sql["longest_word"], conn).to_dict('records')[0]
    full_hex = pd.read_sql_query(sql["full_hex"], conn).to_dict('records')[0]
    full_walls = pd.read_sql_query(sql["full_wall"], conn).to_dict('records')[0]
    full_shelves = pd.read_sql_query(sql["full_shelf"], conn).to_dict('records')[0]
    most_consec_words = pd.read_sql_query(sql["most_consec_words"], conn).to_dict('records')[0]
    largest_words = pd.read_sql_query(sql=sql["words_markup"], con=conn, params=[longest_word["length"]])
    largest_words2 = pd.read_sql_query(sql=sql["words_markup"], con=conn, params=[longest_word["length"]-1])
    largest_words3 = pd.read_sql_query(sql=sql["words_markup"], con=conn, params=[longest_word["length"] - 2])
    hex_completion = pd.read_sql_query(sql["hex_completion"], conn)

    app = Dash()

    app.layout = html.Div(
        [
        html.H1(children="Your Babel Search Stats"),
        html.Tbody([
            html.Tr([
                html.Td([
                    html.H3(children="Total books searched:")
                ]),
                html.Td([
                    html.Div(children=f"{totals["Total_Books"]:,}", style={'text-align': 'right'})
                ]),
                html.Td([

                ], style={'width': 50}),
                html.Td([
                    html.H3(children="Words found > 3 characters: ")
                ], style={'width': 250}),
                html.Td([
                    html.Div(children=total_words, style={'text-align': 'right'})
                ]),
            ]),
            html.Tr([
                html.Td([
                    html.H3(children="Total pages searched:")
                ]),
                html.Td([
                    html.Div(children=f"{totals["Total_Pages"]:,}", style={'text-align': 'right'})
                ]),
                html.Td([

                ]),
                html.Td([
                    html.H3(children="Longest word length: ")
                ]),
                html.Td([
                    html.Div(children=longest_word["length"], style={'text-align': 'right'})
                ]),
            ]),
            html.Tr([
                html.Td([
                    html.H3(children="Full Hexes Searched:")
                ]),
                html.Td([
                    html.Div(children=f"{full_hex["Full_Hexes"]:,}", style={'text-align': 'right'})
                ]),
                html.Td([

                ]),
                html.Td([
                    html.H3(children="Most consecutive words: ")
                ]),
                html.Td([
                    html.Div(children=most_consec_words["amount"], style={'text-align': 'right'})
                ]),
            ]),
            html.Tr([
                html.Td([
                    html.H3(children="Full Walls Searched:")
                ]),
                html.Td([
                    html.Div(children=f"{full_walls["Full_Walls"]:,}", style={'text-align': 'right'})
                ]),
                html.Td([]),
                html.Td([]),
                html.Td([]),
            ]),
            html.Tr([
                html.Td([
                    html.H3(children="Full Shelves Searched:")
                ]),
                html.Td([
                    html.Div(children=f"{full_shelves["Full_Shelves"]:,}", style={'text-align': 'right'})
                ]),
                html.Td([]),
                html.Td([]),
                html.Td([]),
            ]),
        ]),
            html.H2(children=str(longest_word["length"]) + " characters"),
            words_table(largest_words),
            html.H2(children=str(longest_word["length"] - 1) + " characters"),
            words_table(largest_words2),
            html.H2(children=str(longest_word["length"] - 2) + " characters"),
            words_table(largest_words3),
            dcc.Graph(figure=px.bar(hex_completion, x='hex_name', y='Books_Searched'))
        ],
    style = {'marginBottom': 50, 'marginTop': 25},
    )

    app.run(debug=True)

def words_table(data_variable):
    return dash_table.DataTable(data=data_variable.to_dict('records'), sort_action="native",
                         columns=[{'name': 'Word', 'id': 'word_markup', 'type': 'text', 'presentation': 'markdown'},
                                  {'name': 'Title', 'id': 'title'}],
                         style_table={
                             'width': 700,
                         },
                         style_header={
                             "color": "white",
                             "backgroundColor": "#799DBF",
                             "fontWeight": "bold",
                             "textAlign": "center",
                         },
                         style_data={
                             'minWidth': '75px', 'maxWidth': '600px',
                             'overflow': 'hidden',
                             'textOverflow': 'ellipsis',
                             'textAlign': 'left',
                         },
                         page_size=10)
