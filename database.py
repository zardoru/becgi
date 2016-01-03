from math import log10
import os
import psycopg2
from urllib.parse import urlparse


# heroku database_url!
url = urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

class Song(object):
    def __init__(self, name, author, bga_author, description, link, email, id, cnt):
        self.name = name
        self.author = author
        self.bga_author = bga_author
        self.description = description
        self.link = link
        self.email = email
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

def insert_entry(name, author, bga_author, description, link, email):
    c = conn.cursor()
    c.execute("""INSERT INTO entry
    (name,author,bga_author,description,url,email)
    VALUES (%s,%s,%s,%s,%s,%s)""",
              (name, author, bga_author, description, link,email))
    conn.commit()

def get_entries():
    entries = []
    c = conn.cursor()
    c.execute("""
SELECT
    entry.name,
    entry.author,
    entry.bga_author,
    entry.description,
    entry.url,
    entry.email,
    entry.id,
    COUNT(impression.id)
 FROM entry
 LEFT JOIN impression ON entry.id=impression.id
 GROUP BY entry.id;
    """)
    for row in c.fetchall():
        entries.append(Song(*row))

    return entries

def get_impressions(song_id):
    impressions = []
    c = conn.cursor()
    c.execute('SELECT * FROM impression WHERE parent_entry=%s', (song_id,))
    for row in c.fetchall():
        impressions.append(Impression(row[1], row[2], row[3]))
    return impressions

def get_song_by_id(song_id):
    c = conn.cursor()
    c.execute("""
    SELECT
        entry.name,
        entry.author,
        entry.bga_author,
        entry.description,
        entry.url,
        entry.email,
        entry.id,
        COUNT(impression.id)
     FROM entry
     LEFT JOIN impression ON entry.id=impression.id
     WHERE entry.id = %s
     GROUP BY entry.id; """,(song_id,))
    for row in c.fetchall():
        return Song(*row)

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
