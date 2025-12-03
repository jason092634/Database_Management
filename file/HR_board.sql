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
