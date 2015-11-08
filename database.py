import sqlite3
from math import log10

class Song(object):
    def __init__(self, name, author, bga_author, link, id, cnt):
        self.name = name
        self.author = author
        self.bga_author = bga_author
        self.link = link
        self.id = id
        self.impression_count = cnt

class Impression(object):
    def __init__(self, author, rating, comment):
        self.author = author
        self.rating = rating
        self.comment = comment

def get_conn():
    return sqlite3.connect('venue.db')

def generate():
    conn = get_conn()
    c = conn.cursor()

    f = open("database.sql")
    dbq = "\n".join([x for x in f])
    dbq = dbq.split(";")
    for stmt in dbq:
        c.execute(stmt)
    conn.close()

def insert_entry(name, author, bga_author, link):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO entry VALUES (NULL,?,?,?,?)',
              (name, author, bga_author, link))
    conn.commit()
    conn.close()

def get_entries():
    entries = []
    conn = get_conn()
    c = conn.cursor()
    for row in c.execute('SELECT * FROM entry'):
        cnt_cur = conn.cursor()
        for cnt_row in cnt_cur.execute("SELECT COUNT(*) FROM impression WHERE parent_entry=?", (row[0],)):
            entries.append(Song(row[1], row[2], row[3], row[4], row[0], cnt_row[0]))

    conn.close()
    return entries

def get_impressions(song_id):
    impressions = []
    conn = get_conn()
    c = conn.cursor()
    for row in c.execute('SELECT * FROM impression WHERE parent_entry=?',(song_id,)):
        impressions.append(Impression(row[1], row[2], row[3]))
    return impressions

def get_song_by_id(song_id):
    conn = get_conn()
    c = conn.cursor()
    for row in c.execute('SELECT * FROM entry WHERE id=?',(song_id,)):
        cnt_cur = conn.cursor()
        for cnt_row in cnt_cur.execute("SELECT COUNT(*) FROM impression WHERE parent_entry=?", (row[0],)):
            return Song(row[1], row[2], row[3], row[4], row[0], cnt_row[0])

def get_song_rating(song_id):
    impressions = get_impressions(song_id)
    score = sum(int(x.rating) for x in impressions)
    if len(impressions):
        return round(log10(len(impressions) + 1) * score / float(len(impressions)), 2)
    else:
        return 0

def insert_impression(id, author, rating, comment, ip):
    conn = get_conn()
    c = conn.cursor()
    if len(author) == 0:
        author = "Anonymous"

    t = (author, int(rating), comment, id, ip)
    c.execute("INSERT INTO impression VALUES(NULL,?,?,?,?,?)", t)
    conn.commit()
    conn.close()
