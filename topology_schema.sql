CREATE SCHEMA IF NOT EXISTS ipv4_topology AUTHORIZATION postgres
    CREATE TABLE map_address_to_node_id(
	address inet,
	node_id integer
    )
    CREATE TABLE map_address_or_node_id_to_link(
	node_id integer,
	address inet, -- optional
	link_id integer
    )
    CREATE TABLE map_link_to_nodes(
	link_id integer,
	node_id_1 integer,
	interface_1 inet, -- optional
	node_id_2 integer,
	interface_2 inet, -- optional
	relationship text
    )
    CREATE TABLE map_node_id_to_as_number(
	node_id integer,
	as_number integer
    );
