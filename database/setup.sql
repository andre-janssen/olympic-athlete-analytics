-- Alle Tabellen löschen, sofern vorhanden

DROP TABLE IF EXISTS fact_medals;
DROP TABLE IF EXISTS dim_event;
DROP TABLE IF EXISTS dim_countries;
DROP TABLE IF EXISTS dim_medal;
DROP TABLE IF EXISTS dim_athletes;
DROP TABLE IF EXISTS dim_sport;
DROP TABLE IF EXISTS dim_date;


-- Erstellung der Dimensionstabellen
-- Start mit Dimensionstabellen ohne Fremdschlüssel

CREATE TABLE dim_date (
    DateID          integer         PRIMARY KEY,
    year            integer         NOT NULL
);


CREATE TABLE dim_sport (
    SportID         integer         PRIMARY KEY,
    sport           varchar         NOT NULL
);


CREATE TABLE dim_athletes (
    AthleteID       integer         PRIMARY KEY,
    name            varchar         NOT NULL,
    sex             char(1)  
);


CREATE TABLE dim_medal (
    MedalID         integer         PRIMARY KEY,
    medal_name      varchar
);


CREATE TABLE dim_countries (
    CountryID       integer         PRIMARY KEY,
    country_name    varchar,
    NOC_code        varchar
);

-- Dimensionstabellen mit Fremdschlüssel

CREATE TABLE dim_event (
    EventID         integer         PRIMARY KEY,
    SportID         integer         REFERENCES dim_sport(SportID),
    name            varchar
);

-- Faktentabelle

CREATE TABLE fact_medals (
    FactID                  integer         PRIMARY KEY,
    DateID                  integer         REFERENCES dim_date(DateID),
    athlete                 integer         REFERENCES dim_athletes(AthleteID),
    event                   integer         REFERENCES dim_event(EventID),
    medal                   integer         REFERENCES dim_medal(MedalID),
    age_at_event            integer,
    body_size_at_event      integer,
    body_weight_at_event    integer,
    country_at_event        integer         REFERENCES dim_countries(CountryID)
);