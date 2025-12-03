-- User role
CREATE TYPE role_type AS ENUM ('Admin', 'User');

-- Team status
CREATE TYPE team_status AS ENUM ('Active', 'Inactive');

-- Player status, Umpire status
CREATE TYPE career_status AS ENUM ('Active', 'Retired');

-- Pitching role
CREATE TYPE pitching_role AS ENUM ('SP', 'RP', 'CL');

CREATE TABLE "User" (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role role_type DEFAULT 'User',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE League (
    league_id SERIAL PRIMARY KEY,
    league_name VARCHAR(50) UNIQUE NOT NULL
);


CREATE TABLE Team (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(50) NOT NULL,
    manager_name VARCHAR(50) NOT NULL,
    team_status team_status DEFAULT 'Active',
    league_id INT REFERENCES League(league_id)
);

CREATE TABLE Umpire (
    umpire_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    status career_status DEFAULT 'Active'
);

CREATE TABLE Player (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    number INT,
    status career_status DEFAULT 'Active',
    team_id INT REFERENCES Team(team_id)
);

CREATE TABLE Match (
    match_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    start_time TIME,
    location VARCHAR(100),
    home_team_id INT REFERENCES Team(team_id),
    home_score INT DEFAULT 0,
    away_team_id INT REFERENCES Team(team_id),
    away_score INT DEFAULT 0,
    status TEXT DEFAULT 'scheduled',
    weather VARCHAR(50),
    temperature DECIMAL(4,1),
    attendance INT
);

CREATE TABLE Match_Umpire (
    match_id INT REFERENCES Match(match_id),
    umpire_id INT REFERENCES Umpire(umpire_id),
    role VARCHAR(50),
    PRIMARY KEY (match_id, umpire_id)
);

CREATE TABLE Match_Player (
    record_id SERIAL PRIMARY KEY,
    match_id INT REFERENCES Match(match_id),
    player_id INT REFERENCES Player(player_id),
    position VARCHAR(50),
    batting_order INT,
    is_starting BOOLEAN DEFAULT TRUE
);

CREATE TABLE BattingRecord (
    record_id INT PRIMARY KEY REFERENCES Match_Player(record_id),
    at_bats INT DEFAULT 0,
    plate_appearance INT DEFAULT 0,
    hits INT DEFAULT 0,
    doubles INT DEFAULT 0,
    triples INT DEFAULT 0,
    home_runs INT DEFAULT 0,
    strikeouts INT DEFAULT 0,
    walks INT DEFAULT 0,
    hit_by_pitch INT DEFAULT 0,
    sacrifice_flies INT DEFAULT 0,
    double_play INT DEFAULT 0,
    triple_play INT DEFAULT 0,
    rbis INT DEFAULT 0,
    runs INT DEFAULT 0,
    stolen_bases INT DEFAULT 0,
    caught_stealing INT DEFAULT 0,
    remarks VARCHAR(50)
);

CREATE TABLE PitchingRecord (
    record_id INT PRIMARY KEY REFERENCES Match_Player(record_id),
    pitching_role pitching_role,
    pitch_result VARCHAR(10),
    innings_pitched DECIMAL(4,1) DEFAULT 0,
    pitches INT DEFAULT 0,
    batters_faced INT DEFAULT 0,
    strikeouts INT DEFAULT 0,
    walks INT DEFAULT 0,
    hit_batters INT DEFAULT 0,
    hits_allowed INT DEFAULT 0,
    singles INT DEFAULT 0,
    doubles INT DEFAULT 0,
    triples INT DEFAULT 0,
    home_runs INT DEFAULT 0,
    runs_allowed INT DEFAULT 0,
    earned_runs INT DEFAULT 0,
    fly_outs INT DEFAULT 0,
    ground_outs INT DEFAULT 0,
    line_outs INT DEFAULT 0,
    stolen_bases_allowed INT DEFAULT 0,
    wild_pitches INT DEFAULT 0,
    balks INT DEFAULT 0,
    remarks VARCHAR(50)
);


CREATE TABLE FieldingRecord (
    record_id INT PRIMARY KEY REFERENCES Match_Player(record_id),
    fielding_chances INT DEFAULT 0,
    putouts INT DEFAULT 0,
    assists INT DEFAULT 0,
    errors INT DEFAULT 0,
    remarks VARCHAR(50)
);

CREATE TABLE Followed_Player (
    user_id INT REFERENCES "User"(user_id),
    player_id INT REFERENCES Player(player_id),
    follow_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, player_id)
);

CREATE TABLE Followed_Team (
    user_id INT REFERENCES "User"(user_id),
    team_id INT REFERENCES Team(team_id),
    follow_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, team_id)
);