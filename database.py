from math import log10
import psycopg2
from urllib.parse import urlparse
from datetime import datetime
from config import *
from dbtoken import create_token
import logging

# postgres://user:password@server:port/database i think
url = urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)


def from_iso_date(x):
    return datetime.strptime(x, "%Y-%m-%d")


class Scoring(object):
    NONE = 0
    BMWEST_16 = 1


class IncorrectEvent(Exception):
    def __init__(self):
        Exception.__init__(self, "This doesn't correspond to this event.")


class Song(object):
    def __init__(self,
                 name,
                 author,
                 fake_author,
                 bga_author,
                 description,
                 link,
                 email,
                 song_id,
                 event_id,
                 cnt,
                 tok):
        self.name = name
        self.author = author
        self.fake_author = fake_author
        self.bga_author = bga_author
        self.description = description
        self.link = link
        self.email = email
        self.id = song_id
        self.event_id = event_id
        self.impression_count = cnt
        self.token = tok

        evt = Event(event_id)
        if evt.use_fake_name:
            if evt.are_impressions_finished:
                if len(fake_author) > 0:
                    self.display_name = "{} ({})".format(fake_author, author)
                else:
                    self.display_name = author
            else:
                if len(fake_author) > 0:
                    self.display_name = fake_author
                else:
                    self.display_name = author
        else:
            self.display_name = author


class Event:
    def assign_from_row(self, row):
        # database
        self.id = row[0]

        # meta/contact
        self.name = row[1]
        self.description = row[2]
        self.organizers = row[3]
        self.download_package = row[4]
        self.sidebar_content = row[5]
        self.email = row[6]
        self.twitter = row[7]

        # URLs
        self.banner_url = row[8]
        self.css_url = row[9]

        # dates are converted to datetime.date by psycopg
        self.impression_start = row[10]
        self.impression_end = row[11]
        self.submission_start = row[12]
        self.submission_end = row[13]

        # scoring method
        self.scoring_method = int(row[14])

        # flags
        self.use_fake_name = row[15]

        # token
        self.token = row[16]

        return self

    def __init__(self, event_id=None):
        now = datetime.utcnow()
        self.id = event_id
        self.name = ""
        self.description = ""
        self.organizers = ""
        self.download_package = ""
        self.sidebar_content = ""
        self.email = ""
        self.twitter = ""
        self.banner_url = ""
        self.css_url = ""
        self.impression_start = now
        self.impression_end = now
        self.submission_start = now
        self.submission_end = now
        self.scoring_method = Scoring.NONE
        self.use_fake_name = False
        self.token = ""

        if event_id:
            # Create object from id
            c = conn.cursor()
            c.execute("""SELECT * FROM event WHERE id=%s""", (event_id,))
            rows = c.fetchall()
            if len(rows) > 0:
                for row in rows:
                    self.assign_from_row(row)
            else:
                raise IncorrectEvent()

    @property
    def are_submissions_open(self):
        if not DEBUG:
            return self.submission_start <= datetime.utcnow() <= self.submission_end
        else:
            return True

    @property
    def allow_blank_comments(self):
        if self.scoring_method == Scoring.NONE:
            return False
        return True

    @property
    def are_impressions_open(self):
        if not DEBUG:
            return self.impression_start <= datetime.utcnow() <= self.impression_end
        else:
            return True

    @property
    def can_see_submissions(self):
        if not DEBUG:
            return self.submission_start <= datetime.utcnow()
        else:
            return True

    @property
    def are_impressions_finished(self):
        if not DEBUG:
            return datetime.utcnow() >= self.submission_end
        else:
            return True

    @property
    def entries(self):
        entries = []
        c = conn.cursor()
        c.execute("""
    SELECT
        entry.name,
        entry.author,
        entry.fake_author,
        entry.bga_author,
        entry.description,
        entry.url,
        entry.email,
        entry.id,
        entry.event_id,
        COUNT(impression.id),
        entry.token
     FROM entry
     LEFT JOIN impression ON entry.id=impression.parent_entry
     WHERE entry.event_id=%s
     GROUP BY entry.id;
        """, (self.id,))
        for row in c.fetchall():
            entries.append(Song(*row))

        return entries

    def insert_entry(self, name, author, fake_author, bga_author, description, link, email):
        c = conn.cursor()
        tok = create_token()

        c.execute("""INSERT INTO entry
        (event_id, name,author,fake_author,bga_author,description,url,email,token)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                  (self.id, name, author, fake_author, bga_author, description, link, email, tok))
        conn.commit()
        return tok

    def update_entry(self, name, author, fake_author, bga_author, description, link, email, sid, tok):
        c = conn.cursor()
        c.execute("""UPDATE entry SET
                    name=%s,
                    author=%s,
                    fake_author=%s,
                    bga_author=%s,
                    description=%s,
                    url=%s,
                    email=%s
                    WHERE id=%s AND token=%s""", (name,
                                                  author,
                                                  fake_author,
                                                  bga_author,
                                                  description,
                                                  link,
                                                  email,
                                                  sid, tok))
        conn.commit()

    def get_impressions(self, song):
        if song.event_id == self.id:
            impressions = []
            c = conn.cursor()
            c.execute('SELECT * FROM impression WHERE parent_entry=%s', (song.id,))
            for row in c.fetchall():
                impressions.append(Impression(row[1], row[2], row[3]))
            return impressions
        else:
            raise IncorrectEvent()

    def get_song_rating(self, song_id):
        impressions = self.get_impressions(song_id)
        return self.get_rating_impressions(impressions)

    def get_rating_impressions(self, impressions):
        if self.scoring_method == Scoring.BMWEST_16:
            return self.bmwest_scoring(impressions)
        else:
            return 0

    def bmwest_scoring(self, impressions):
        score = sum(int(x.rating) for x in impressions)
        if len(impressions):
            return round(log10(len(impressions) + 1) * score / float(len(impressions)), 2)
        else:
            return 0

    def normalize_scoring(self, rating):
        if self.scoring_method == Scoring.BMWEST_16:
            rating = int(rating)
            if rating < 0 or rating > 100:
                raise ValueError("Rating is out of range.")
        else:
            rating = 0

        return rating

    def insert_impression(self, song_id, author, rating, comment, ip):
        rating = self.normalize_scoring(rating)

        c = conn.cursor()
        if len(author) == 0:
            author = "Anonymous"

        if get_song_by_id(song_id).event_id == self.id:
            t = (author, int(rating), comment, song_id, ip)
            c.execute("""INSERT INTO impression
            (author, rating, comment, parent_entry, ip)
            VALUES(%s,%s,%s,%s,%s)""", t)
            conn.commit()
        else:
            raise IncorrectEvent()


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


def get_events():
    c = conn.cursor()
    c.execute("""SELECT * FROM event""")
    return [Event().assign_from_row(row) for row in c.fetchall()]


def get_song_by_id(song_id):
    c = conn.cursor()
    c.execute("""
    SELECT
        entry.name,
        entry.author,
        entry.fake_author,
        entry.bga_author,
        entry.description,
        entry.url,
        entry.email,
        entry.id,
        entry.event_id,
        COUNT(impression.id),
        entry.token
     FROM entry
     LEFT JOIN impression ON entry.id=impression.parent_entry
     WHERE entry.id = %s
     GROUP BY entry.id; """, (song_id,))
    for row in c.fetchall():
        return Song(*row)
    return None


def get_song_by_token_and_id(token, song_id):
    c = conn.cursor()
    c.execute("""
    SELECT
        entry.name,
        entry.author,
        entry.fake_author,
        entry.bga_author,
        entry.description,
        entry.url,
        entry.email,
        entry.id,
        entry.event_id,
        COUNT(impression.id),
        entry.token
     FROM entry
     LEFT JOIN impression ON entry.id=impression.parent_entry
     WHERE entry.token = %s AND entry.id = %s
     GROUP BY entry.id; """, (token, song_id))
    for row in c.fetchall():
        return Song(*row)
    return None


def from_scoring_name(x):  # must match the values at form
    if x == "bmwest2016":
        return Scoring.BMWEST_16
    else:
        return Scoring.NONE


def update_event(*row):
    c = conn.cursor()
    row = list(row)
    row[12] = from_scoring_name(row[12])
    row = tuple(row)
    c.execute("""UPDATE event SET
              name=%s,
              description=%s,
              organizers=%s,
              download_url=%s,
              email=%s,
              twitter_handle=%s,
              banner_url=%s,
              css_url=%s,
              impression_start=%s,
              impression_end=%s,
              submission_start=%s,
              submission_end=%s,
              scoring_method=%s,
              use_fake_name=%s
              WHERE id=%s AND token=%s
              """, row)
    logging.info(row)
    conn.commit()
    return None
