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
