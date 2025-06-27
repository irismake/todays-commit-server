CREATE TABLE "user" (
  "user_id" INTEGER PRIMARY KEY,
  "user_name" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL
);

CREATE TABLE "grass" (
  "user_id" INTEGER NOT NULL,
  "map_id" INTEGER NOT NULL,
  "commit_count" INTEGER NOT NULL,
  PRIMARY KEY ("user_id", "map_id"),
  FOREIGN KEY ("user_id") REFERENCES "user" ("user_id"),
  FOREIGN KEY ("map_id") REFERENCES "map" ("map_id")
);

CREATE TABLE "map" (
  "map_id" INTEGER PRIMARY KEY,
  "map_code" INTEGER NOT NULL,
  "zone_code" INTEGER NOT NULL,
  "x" INTEGER NOT NULL,
  "y" INTEGER NOT NULL
);

CREATE TABLE "commit" (
  "id" INTEGER NOT NULL,
  "map_id" INTEGER NOT NULL,
  "user_id" INTEGER NOT NULL,
  "created_at" TIMESTAMP NOT NULL,
  PRIMARY KEY ("id", "map_id", "user_id"),
  FOREIGN KEY ("map_id") REFERENCES "map" ("map_id"),
  FOREIGN KEY ("user_id") REFERENCES "user" ("user_id")
);

CREATE TABLE "subzone" (
  "map_id" INTEGER PRIMARY KEY,
  "sub_zone_code" INTEGER NOT NULL,
  FOREIGN KEY ("map_id") REFERENCES "map" ("map_id")
);
