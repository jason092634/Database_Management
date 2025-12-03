-- 輸入「球員名字 + 賽季」→ 該季打擊 / 投球 / 守備成績（加總）
--   %s = 球員名字，例如 'Shohei Ohtani'
--   %s = 賽季年份，例如 2025
SELECT
    p.player_id,
    p.name AS player_name,
    EXTRACT(YEAR FROM m.date) AS season_year,

    -- 打擊成績總和
    SUM(COALESCE(b.at_bats, 0))           AS total_at_bats,
    SUM(COALESCE(b.plate_appearance, 0))  AS total_plate_appearance,
    SUM(COALESCE(b.hits, 0))              AS total_hits,
    SUM(COALESCE(b.doubles, 0))           AS total_doubles,
    SUM(COALESCE(b.triples, 0))           AS total_triples,
    SUM(COALESCE(b.home_runs, 0))         AS total_home_runs,
    SUM(COALESCE(b.rbis, 0))              AS total_rbis,
    SUM(COALESCE(b.runs, 0))              AS total_runs,
    SUM(COALESCE(b.strikeouts, 0))        AS total_batting_strikeouts,
    SUM(COALESCE(b.walks, 0))             AS total_walks,
    SUM(COALESCE(b.hit_by_pitch, 0))      AS total_hbp,
    SUM(COALESCE(b.stolen_bases, 0))      AS total_stolen_bases,
    SUM(COALESCE(b.caught_stealing, 0))   AS total_caught_stealing,

    -- 投球成績總和
    SUM(COALESCE(pr.innings_pitched, 0))  AS total_innings_pitched,
    SUM(COALESCE(pr.pitches, 0))          AS total_pitches,
    SUM(COALESCE(pr.batters_faced, 0))    AS total_batters_faced,
    SUM(COALESCE(pr.strikeouts, 0))       AS total_pitching_strikeouts,
    SUM(COALESCE(pr.walks, 0))            AS total_pitching_walks,
    SUM(COALESCE(pr.hits_allowed, 0))     AS total_hits_allowed,
    SUM(COALESCE(pr.home_runs, 0))        AS total_pitching_home_runs,
    SUM(COALESCE(pr.runs_allowed, 0))     AS total_runs_allowed,
    SUM(COALESCE(pr.earned_runs, 0))      AS total_earned_runs,

    -- 守備成績總和
    SUM(COALESCE(f.fielding_chances, 0))  AS total_fielding_chances,
    SUM(COALESCE(f.putouts, 0))           AS total_putouts,
    SUM(COALESCE(f.assists, 0))           AS total_assists,
    SUM(COALESCE(f.errors, 0))            AS total_errors

FROM player p
JOIN match_player mp
    ON mp.player_id = p.player_id
JOIN match m
    ON m.match_id = mp.match_id
LEFT JOIN battingrecord b
    ON b.record_id = mp.record_id
LEFT JOIN pitchingrecord pr
    ON pr.record_id = mp.record_id
LEFT JOIN fieldingrecord f
    ON f.record_id = mp.record_id
WHERE p.name = %s
  AND EXTRACT(YEAR FROM m.date) = %s
GROUP BY
    p.player_id, p.name, EXTRACT(YEAR FROM m.date);
