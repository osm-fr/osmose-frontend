alter table dynpoi_status add foreign key (source) references dynpoi_source(source);
alter table marker add foreign key (source) references dynpoi_source(source);
