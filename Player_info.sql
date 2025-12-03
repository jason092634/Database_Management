-- 輸入球員名字 → 球員相關資訊
SELECT
    p.player_id,
    p.name AS player_name,
    p.number,
    p.status,
    t.team_name,
    t.manager_name,
    l.league_name
FROM player p
LEFT JOIN team t ON p.team_id = t.team_id
LEFT JOIN league l ON t.league_id = l.league_id
WHERE p.name = 'Shohei Ohtani';

