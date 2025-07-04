-- 1. 지도 정보
CREATE TABLE map (
    map_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    map_level SMALLINT,
    map_code BIGINT
);

-- 2. 셀 정보 (map 내 local id)
CREATE TABLE cell (
    cell_id SMALLINT NOT NULL,
    map_id SMALLINT NOT NULL,
    zone_code INTEGER,
    x SMALLINT NOT NULL,
    y SMALLINT NOT NULL,
    PRIMARY KEY (cell_id, map_id),
    FOREIGN KEY (map_id) REFERENCES map(map_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- 3. 셀 단위 유닛 (예: 공간 단위 추가 정보)
CREATE TABLE unit (
    unit_code BIGINT PRIMARY KEY,
    cell_id SMALLINT NOT NULL,
    map_id SMALLINT NOT NULL,
    FOREIGN KEY (cell_id, map_id) REFERENCES cell(cell_id, map_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- 4. 사용자 정보
CREATE TABLE "user" (
    user_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. 장소 정보 (PNU 기준 단일 공간 단위)
CREATE TABLE place (
    pnu BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL
);

-- 6. 커밋 기록 (유저가 PNU에 커밋한 기록)
CREATE TABLE "commit" (
    commit_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    pnu BIGINT NOT NULL,
    user_id SMALLINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_private BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (pnu) REFERENCES place(pnu) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- 7. 커밋과 셀을 연결하는 다대다 매핑
CREATE TABLE grass (
    grass_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    commit_id BIGINT NOT NULL,
    cell_id SMALLINT NOT NULL,
    map_id SMALLINT NOT NULL,
    FOREIGN KEY (commit_id) REFERENCES "commit"(commit_id) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (cell_id, map_id) REFERENCES cell(cell_id, map_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- 8. 셀 단위 커밋 집계 뷰
CREATE VIEW grass_view AS
SELECT
    map_id,
    cell_id,
    COUNT(*) AS commit_count
FROM grass
GROUP BY map_id, cell_id;


-- grass: 셀 기준 커밋 필터링
CREATE INDEX idx_grass_cell ON grass (cell_id, map_id);

-- commit: pnu 조인 성능 향상
CREATE INDEX idx_commit_pnu ON "commit" (pnu);

-- commit: 유저 + PNU를 같이 조회할 경우
CREATE INDEX idx_commit_user_pnu ON "commit" (user_id, pnu);