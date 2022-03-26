drop table if exists entries;
create table entries (
id integer primary key autoincrement,
author text not null,
coauthor text not null
);