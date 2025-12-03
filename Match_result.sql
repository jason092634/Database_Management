-- 輸入日期 → 當天所有比賽資訊和結果
-- 輸入：%s = 日期（DATE），例如 '2025-3-19'
SELECT
    m.match_id,
    m.date,
    m.start_time,
    m.location,
    m.status,
    m.weather,
    m.temperature,
    m.attendance,
    ht.team_name AS home_team_name,
    m.home_score,
    at.team_name AS away_team_name,
    m.away_score
FROM match m
JOIN team ht ON m.home_team_id = ht.team_id
JOIN team at ON m.away_team_id = at.team_id
WHERE m.date = %s
ORDER BY m.start_time, m.match_id;

-- 輸入日期 & 球隊 → 該隊該天比賽結果 + 兩隊所有球員當天細項
-- 輸入：
--   %s = 日期（DATE）
--   %s = 球隊名稱 (team_name)
SELECT
    -- 比賽資訊
    m.match_id,
    m.date,
    m.start_time,
    m.location,
    m.status,
    m.weather,
    m.temperature,
    m.attendance,
    ht.team_name AS home_team_name,
    m.home_score,
    at.team_name AS away_team_name,
    m.away_score,

    -- 出場球員資訊
    p.player_id,
    p.name       AS player_name,
    p.number,
    p.status     AS player_status,
    pt.team_name AS player_team_name,
    mp.position,
    mp.batting_order,
    mp.is_starting,

    -- 打擊成績（這場）
    b.at_bats,
    b.plate_appearance,
    b.hits,
    b.doubles,
    b.triples,
    b.home_runs,
    b.rbis,
    b.runs,
    b.strikeouts     AS batting_strikeouts,
    b.walks          AS batting_walks,
    b.hit_by_pitch,
    b.stolen_bases,
    b.caught_stealing,

    -- 投球成績（這場）
    pr.pitching_role,
    pr.innings_pitched,
    pr.pitches,
    pr.batters_faced,
    pr.strikeouts    AS pitching_strikeouts,
    pr.walks         AS pitching_walks,
    pr.hits_allowed,
    pr.home_runs     AS pitching_home_runs,
    pr.runs_allowed,
    pr.earned_runs,

    -- 守備成績（這場）
    f.fielding_chances,
    f.putouts,
    f.assists,
    f.errors

FROM match m
JOIN team ht ON m.home_team_id = ht.team_id
JOIN team at ON m.away_team_id = at.team_id

JOIN match_player mp
    ON mp.match_id = m.match_id
JOIN player p
    ON p.player_id = mp.player_id
LEFT JOIN team pt
    ON pt.team_id = p.team_id

LEFT JOIN battingrecord b
    ON b.record_id = mp.record_id
LEFT JOIN pitchingrecord pr
    ON pr.record_id = mp.record_id
LEFT JOIN fieldingrecord f
    ON f.record_id = mp.record_id

WHERE m.date = '2025-3-19'
  AND (ht.team_name = %s OR at.team_name = %s)
ORDER BY
    m.match_id,
    pt.team_name,
    mp.batting_order,
    p.player_id;

-- 輸入球隊 → 該球隊所有比賽資訊和結果
-- 輸入：%s = 球隊名稱
SELECT
    m.match_id,
    m.date,
    m.start_time,
    m.location,
    m.status,
    ht.team_name AS home_team_name,
    m.home_score,
    at.team_name AS away_team_name,
    m.away_score,
    CASE
        WHEN ht.team_name = %s AND m.home_score > m.away_score THEN 'Win'
        WHEN at.team_name = %s AND m.away_score > m.home_score THEN 'Win'
        WHEN m.home_score = m.away_score THEN 'Tie'
        ELSE 'Loss'
    END AS result_for_team
FROM match m
JOIN team ht ON m.home_team_id = ht.team_id
JOIN team at ON m.away_team_id = at.team_id
WHERE ht.team_name = %s
   OR at.team_name = %s
ORDER BY m.date, m.start_time, m.match_id;

-- 打擊率排行榜（AVG） Top 5 
-- 定義：AVG = hits / at_bats，且至少 30 打席（可以隨意修改）
SELECT
    s.player_id,
    s.player_name,
    s.team_name,
    s.total_hits,
    s.total_at_bats,
    ROUND(s.total_hits::numeric / NULLIF(s.total_at_bats, 0), 3) AS avg,
    RANK() OVER (
        ORDER BY s.total_hits::numeric / NULLIF(s.total_at_bats, 0) DESC
    ) AS rank
FROM (
    SELECT
        p.player_id,
        p.name AS player_name,
        t.team_name,
        SUM(COALESCE(b.hits, 0)) AS total_hits,
        SUM(COALESCE(b.at_bats, 0)) AS total_at_bats
    FROM player p
    JOIN match_player mp ON mp.player_id = p.player_id
    JOIN match m ON m.match_id = mp.match_id
    LEFT JOIN battingrecord b ON b.record_id = mp.record_id
    LEFT JOIN team t ON t.team_id = p.team_id
    WHERE EXTRACT(YEAR FROM m.date) = 2025
    GROUP BY p.player_id, p.name, t.team_name
) s
WHERE s.total_at_bats >= 30
ORDER BY avg DESC
LIMIT 5;

-- 打擊率排行榜（AVG） Top 5 
-- 定義：AVG = hits / at_bats，且至少 30 打席（可以隨意修改）
SELECT
    s.player_id,
    s.player_name,
    s.team_name,
    s.total_hits,
    s.total_at_bats,
    ROUND(s.total_hits::numeric / NULLIF(s.total_at_bats, 0), 3) AS avg,
    RANK() OVER (
        ORDER BY s.total_hits::numeric / NULLIF(s.total_at_bats, 0) DESC
    ) AS rank
FROM (
    SELECT
        p.player_id,
        p.name AS player_name,
        t.team_name,
        SUM(COALESCE(b.hits, 0)) AS total_hits,
        SUM(COALESCE(b.at_bats, 0)) AS total_at_bats
    FROM player p
    JOIN match_player mp ON mp.player_id = p.player_id
    JOIN match m ON m.match_id = mp.match_id
    LEFT JOIN battingrecord b ON b.record_id = mp.record_id
    LEFT JOIN team t ON t.team_id = p.team_id
    WHERE EXTRACT(YEAR FROM m.date) = 2025
    GROUP BY p.player_id, p.name, t.team_name
) s
WHERE s.total_at_bats >= 30
ORDER BY avg DESC
LIMIT 5;

-- -- 全壘打排行榜（HR） Top 5
SELECT
    p.player_id,
    p.name AS player_name,
    t.team_name,
    SUM(COALESCE(b.home_runs, 0)) AS total_hr,
    RANK() OVER (
        ORDER BY SUM(COALESCE(b.home_runs, 0)) DESC
    ) AS rank
FROM player p
JOIN match_player mp ON mp.player_id = p.player_id
JOIN match m ON m.match_id = mp.match_id
LEFT JOIN battingrecord b ON b.record_id = mp.record_id
LEFT JOIN team t ON t.team_id = p.team_id
WHERE EXTRACT(YEAR FROM m.date) = 2025
GROUP BY p.player_id, p.name, t.team_name
ORDER BY total_hr DESC
LIMIT 5;

-- ERA 排行 Top 5
-- 定義：ERA = 9 × 自責分 / 投球局數，且只顯示至少投 10 局的投手
SELECT
    p.player_id,
    p.name AS player_name,
    t.team_name,
    SUM(COALESCE(pr.innings_pitched, 0)) AS total_ip,
    SUM(COALESCE(pr.earned_runs, 0)) AS total_er,
    ROUND(
        9 * SUM(COALESCE(pr.earned_runs, 0))::numeric
        / NULLIF(SUM(COALESCE(pr.innings_pitched, 0)), 0),
        2
    ) AS era,
    RANK() OVER (
        ORDER BY
            9 * SUM(COALESCE(pr.earned_runs, 0))::numeric
            / NULLIF(SUM(COALESCE(pr.innings_pitched, 0)), 0)
    ) AS rank
FROM player p
JOIN match_player mp ON mp.player_id = p.player_id
JOIN match m ON m.match_id = mp.match_id
LEFT JOIN pitchingrecord pr ON pr.record_id = mp.record_id
LEFT JOIN team t ON t.team_id = p.team_id
WHERE EXTRACT(YEAR FROM m.date) = 2025
GROUP BY p.player_id, p.name, t.team_name
HAVING SUM(COALESCE(pr.innings_pitched, 0)) >= 10
ORDER BY era ASC
LIMIT 5;

-- 球隊勝率排行榜 Top 5
-- 定義：勝率 = wins / games，這個定義可以再延申，因爲如果只打一場比賽且獲勝，它的勝率為1是最高的，感覺有bug
WITH team_games AS (
    SELECT
        t.team_id,
        t.team_name,
        CASE
            WHEN m.home_team_id = t.team_id THEN m.home_score
            ELSE m.away_score
        END AS team_score,
        CASE
            WHEN m.home_team_id = t.team_id THEN m.away_score
            ELSE m.home_score
        END AS opp_score
    FROM team t
    JOIN match m
      ON m.home_team_id = t.team_id
      OR m.away_team_id = t.team_id
    WHERE EXTRACT(YEAR FROM m.date) = 2025
),
team_summary AS (
    SELECT
        team_id,
        team_name,
        COUNT(*) AS games,
        SUM(CASE WHEN team_score > opp_score THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN team_score < opp_score THEN 1 ELSE 0 END) AS losses,
        SUM(CASE WHEN team_score = opp_score THEN 1 ELSE 0 END) AS ties
    FROM team_games
    GROUP BY team_id, team_name
)
SELECT
    team_id,
    team_name,
    games,
    wins,
    losses,
    ties,
    ROUND(wins::numeric / NULLIF(games, 0), 3) AS win_pct
FROM team_summary
ORDER BY win_pct DESC
LIMIT 5;
