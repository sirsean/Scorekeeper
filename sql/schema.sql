
create table league (
    id int(11) not null auto_increment,
    name varchar(255) not null,
    password varchar(255) not null,
    primary key (id)
) engine=InnoDB default charset=utf8;

create table player (
    id int(11) not null auto_increment,
    league_id int(11) not null,
    name varchar(255) not null,
    primary key (id),
    foreign key (league_id) references league(id)
) engine=InnoDB default charset=utf8;

create table location (
    id int(11) not null auto_increment,
    league_id int(11) not null,
    name varchar(255) not null,
    primary key (id),
    foreign key (league_id) references league(id)
) engine=InnoDB default charset=utf8;

create table game (
    id int(11) not null auto_increment,
    location_id int(11) not null,
    start_time timestamp not null default NOW(),
    primary key (id),
    foreign key (location_id) references location(id)
) engine=InnoDB default charset=utf8;

create table game_players (
    game_id int(11) not null,
    player_id int (11) not null,
    primary key (game_id, player_id),
    foreign key (game_id) references game(id),
    foreign key (player_id) references player(id)
) engine=InnoDB default charset=utf8;

create table game_score (
    id int(11) not null auto_increment,
    game_id int(11) not null,
    start_time timestamp not null default NOW(),
    primary key (id),
    foreign key (game_id) references game(id)
) engine=InnoDB default charset=utf8;

create table player_game_score (
    id int(11) not null auto_increment,
    game_score_id int(11) not null,
    player_id int(11) not null,
    score int(11) not null default 0,
    primary key (id),
    foreign key (game_score_id) references game_score(id),
    foreign key (player_id) references player(id)
) engine=InnoDB default charset=utf8;

