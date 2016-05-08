CREATE TABLE IF NOT EXISTS event (
  id SERIAL PRIMARY KEY,
  name varchar(255) NOT NULL UNIQUE,
  description text DEFAULT '',
  organizers text DEFAULT '',
  download_url text DEFAULT '',
  sidebar_content text DEFAULT '',
  email text DEFAULT '',
  twitter_handle text DEFAULT '',
  banner_url text DEFAULT '',
  css_url text DEFAULT '',
  impression_start date NOT NULL DEFAULT NOW(),
  impression_end date NOT NULL DEFAULT NOW(),
  submission_start date NOT NULL DEFAULT NOW(),
  submission_end date NOT NULL DEFAULT NOW(),
  scoring_method INTEGER DEFAULT 0,
  use_fake_name boolean DEFAULT FALSE,
  token text UNIQUE
);

CREATE TABLE IF NOT EXISTS entry (
  id SERIAL PRIMARY KEY,
  name text,
  author text,
  fake_author text,
  bga_author text,
  description text,
  url text,
  email text,
  event_id INTEGER NOT NULL,
  token text,
  FOREIGN KEY(event_id) REFERENCES event(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS impression (
  id SERIAL PRIMARY KEY,
  author varchar(255),
  rating INTEGER,
  comment varchar(1024),
  parent_entry INTEGER NOT NULL,
  ip varchar(255),
  FOREIGN KEY(parent_entry) REFERENCES entry(id) ON DELETE CASCADE
);
