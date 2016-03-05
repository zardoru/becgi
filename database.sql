CREATE TABLE IF NOT EXISTS event (
  id SERIAL PRIMARY KEY,
  name varchar(255) UNIQUE,
  description text,
  organizers text,
  download_url text,
  sidebar_content text,
  email text,
  twitter_handle text,
  banner_url text,
  css_url text,
  impression_start date,
  impression_end date,
  submission_start date,
  submission_end date,
  scoring_method INTEGER,
  use_fake_name boolean
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
  event_id INTEGER,
  FOREIGN KEY(event_id) REFERENCES event(id)
);

CREATE TABLE IF NOT EXISTS impression (
  id SERIAL PRIMARY KEY,
  author varchar(255),
  rating INTEGER CHECK (rating >= 0 AND rating <= 100),
  comment varchar(1024),
  parent_entry INTEGER,
  ip varchar(255),
  FOREIGN KEY(parent_entry) REFERENCES entry(id)
);
