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
