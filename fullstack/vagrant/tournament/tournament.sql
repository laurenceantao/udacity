-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


CREATE TABLE players (id serial primary key, name text);

CREATE TABLE matches (id serial primary key, winner serial references players(id), loser serial references players(id));

CREATE VIEW player_wins as SELECT players.id, coalesce(count(matches.winner),0) as wins from players left join matches on matches.winner = players.id group by players.id;
CREATE VIEW player_losses as SELECT players.id, coalesce(count(matches.loser),0) as losses from players left join matches on matches.loser = players.id group by players.id;