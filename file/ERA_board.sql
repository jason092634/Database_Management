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
