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

