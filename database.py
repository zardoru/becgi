from math import log10
import os
import psycopg2
from urllib.parse import urlparse

url = urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

class Song(object):
    def __init__(self, name, author, bga_author, description, link, id, cnt):
        self.name = name
        self.author = author
        self.bga_author = bga_author
        self.description = description
        self.link = link
        self.id = id
        self.impression_count = cnt

class Impression(object):
    def __init__(self, author, rating, comment):
        self.author = author
        self.rating = rating
        self.comment = comment

def generate():
    c = conn.cursor()
    f = open("database.sql")
    c.execute(f.read())
    conn.commit()

def insert_entry(name, author, bga_author, description, link):
    c = conn.cursor()
    c.execute("""INSERT INTO entry
    (name,author,bga_author,description,url)
    VALUES (%s,%s,%s,%s,%s)""",
              (name, author, bga_author, description, link))
    conn.commit()

def get_entries():
    entries = []
    c = conn.cursor()
    c.execute('SELECT * FROM entry')
    for row in c.fetchmany():
        cnt_cur = conn.cursor()
        cnt_cur.execute("SELECT COUNT(*) FROM impression WHERE parent_entry=%s", (row[0],))
        for cnt_row in cnt_cur.fetchmany():
            entries.append(Song(row[1], row[2], row[3], row[4], row[5], row[0], cnt_row[0]))

    return entries

def get_impressions(song_id):
    impressions = []
    c = conn.cursor()
    c.execute('SELECT * FROM impression WHERE parent_entry=%s', (song_id,))
    for row in c.fetchmany():
        impressions.append(Impression(row[1], row[2], row[3]))
    return impressions

def get_song_by_id(song_id):
    c = conn.cursor()
    c.execute('SELECT * FROM entry WHERE id=%s',(song_id,))
    for row in c.fetchmany():
        cnt_cur = conn.cursor()
        cnt_cur.execute("""SELECT COUNT(*) FROM impression
        WHERE parent_entry=%s""" , (row[0],))
        for cnt_row in cnt_cur.fetchmany():
            return Song(row[1], row[2], row[3], row[4], row[5], row[0], cnt_row[0])

def get_song_rating(song_id):
    impressions = get_impressions(song_id)
    score = sum(int(x.rating) for x in impressions)
    if len(impressions):
        return round(log10(len(impressions) + 1) * score / float(len(impressions)), 2)
    else:
        return 0

def insert_impression(id, author, rating, comment, ip):
    c = conn.cursor()
    if len(author) == 0:
        author = "Anonymous"

    t = (author, int(rating), comment, id, ip)
    c.execute("""INSERT INTO impression
    (author, rating, comment, parent_entry, ip)
    VALUES(%s,%s,%s,%s,%s)""", t)
    conn.commit()
