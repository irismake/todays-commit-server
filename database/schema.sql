PRAGMA foreign_keys = ON;

CREATE TABLE "user" (
  user_id INTEGER NOT NULL,
  user_name TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  PRIMARY KEY (user_id)
);

CREATE TABLE "map" (
  map_id INTEGER NOT NULL,
  map_code INTEGER NOT NULL,
  zone_code INTEGER NOT NULL,
  x INTEGER NOT NULL,
  y INTEGER NOT NULL,
  PRIMARY KEY (map_id)
);

CREATE TABLE "place" (
  pnu INTEGER NOT NULL,
  name TEXT NOT NULL,
  PRIMARY KEY (pnu)
);

CREATE TABLE "grass" (
  grass_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  map_id INTEGER NOT NULL,
  pnu2 INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL,
  PRIMARY KEY (grass_id, user_id, map_id, pnu2),
  FOREIGN KEY (user_id) REFERENCES "user"(user_id),
  FOREIGN KEY (map_id) REFERENCES "map"(map_id),
  FOREIGN KEY (pnu2) REFERENCES "place"(pnu)
);

CREATE VIEW grass_view AS
SELECT
  m.map_id,
  m.map_code,
  m.x,
  m.y,
  COUNT(c.grass_id) AS grass_count
FROM map m
LEFT JOIN "grass" c ON m.map_id = c.map_id
GROUP BY m.map_id, m.map_code, m.x, m.y;
