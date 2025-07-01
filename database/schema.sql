PRAGMA foreign_keys = ON;

CREATE TABLE user (
  user_id INTEGER NOT NULL PRIMARY KEY,
  user_name TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE map (
  map_id INTEGER NOT NULL PRIMARY KEY,
  map_code INTEGER NOT NULL,
  zone_code INTEGER NOT NULL,
  x INTEGER NOT NULL,
  y INTEGER NOT NULL
);

CREATE TABLE grass (
  grass_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  map_id INTEGER NOT NULL,
  pnu INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL,
  PRIMARY KEY (grass_id, user_id, map_id, pnu),
  FOREIGN KEY (user_id) REFERENCES user(user_id),
  FOREIGN KEY (map_id) REFERENCES map(map_id),
  FOREIGN KEY (pnu) REFERENCES place(pnu)
);

CREATE TABLE place (
  pnu INTEGER NOT NULL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE subzone (
  sub_zone_code INTEGER NOT NULL,
  map_id INTEGER NOT NULL,
  PRIMARY KEY (sub_zone_code, map_id),
  FOREIGN KEY (map_id) REFERENCES map(map_id)
);

CREATE VIEW grass_view AS
SELECT
  m.map_id,
  m.map_code,
  m.x,
  m.y,
  COUNT(g.grass_id) AS commit_count
FROM map m
LEFT JOIN grass g ON m.map_id = g.map_id
GROUP BY m.map_id, m.map_code, m.x, m.y;


CREATE INDEX idx_grass_map_id ON grass(map_id);
CREATE INDEX idx_grass_pnu ON grass(map_id, pnu);