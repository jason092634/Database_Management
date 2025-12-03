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
