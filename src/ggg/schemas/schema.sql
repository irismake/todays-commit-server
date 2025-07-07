-- 1. map 테이블
CREATE TABLE map (
    map_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    map_level SMALLINT,
    map_code BIGINT
);

-- 2. coord 테이블
CREATE TABLE coord (
    x SMALLINT NOT NULL,
    y SMALLINT NOT NULL,
    PRIMARY KEY (x, y)
);

-- 3. cell 테이블
CREATE TABLE cell (
    cell_id SMALLINT NOT NULL,
    map_id SMALLINT NOT NULL,
    zone_code INTEGER,
    x SMALLINT NOT NULL,
    y SMALLINT NOT NULL,
    PRIMARY KEY (cell_id, map_id),
    FOREIGN KEY (map_id) REFERENCES map(map_id) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (x, y) REFERENCES coord(x, y) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- 4. unit 테이블
CREATE TABLE unit (
    unit_code BIGINT PRIMARY KEY,
    cell_id SMALLINT NOT NULL,
    map_id SMALLINT NOT NULL,
    FOREIGN KEY (cell_id, map_id) REFERENCES cell(cell_id, map_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- 5. user 테이블
CREATE TABLE "user" (
    user_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    provider VARCHAR(20) NOT NULL,
    provider_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (provider, provider_id)
);

-- 6. place 테이블
CREATE TABLE place (
    pnu BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL
);

-- 7. commit 테이블
CREATE TABLE "commit" (
    commit_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    pnu BIGINT NOT NULL,
    user_id SMALLINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pnu) REFERENCES place(pnu) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- 8. grass 테이블
CREATE TABLE grass (
    grass_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    commit_id BIGINT NOT NULL,
    cell_id SMALLINT NOT NULL,
    map_id SMALLINT NOT NULL,
    FOREIGN KEY (commit_id) REFERENCES "commit"(commit_id) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (cell_id, map_id) REFERENCES cell(cell_id, map_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- 🔍 인덱스 생성
CREATE INDEX idx_grass_cell ON grass (cell_id, map_id);
CREATE INDEX idx_commit_pnu ON "commit" (pnu);
CREATE INDEX idx_commit_user_pnu ON "commit" (user_id, pnu);