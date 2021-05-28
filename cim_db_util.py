#!/usr/bin/python3

import os, cim_util, subprocess, datetime, re, pyodbc, sqlite3
from argparse import ArgumentParser

def connect_ip_version(ipv4=True):

    if ipv4 is True:
        cnxn = sqlite3.connect('ipv4_topo.db')
    else:
        cnxn = sqlite3.connect('ipv6_topo.db')

    return cnxn

# Create schemas and tables
def create_tables(cursor):
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS map_address_to_node(
        address TEXT,
        node_id INTEGER
    );
    """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS map_link_to_nodes(
            link_id INTEGER,
            node_id_1 INTEGER,
            address_1 TEXT DEFAULT NULL, -- optional
            node_id_2 INTEGER,
            address_2 TEXT DEFAULT NULL, -- optional
            relationship TEXT DEFAULT NULL
        );
        """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS map_node_to_asn(
            node_id INTEGER,
            as_number INTEGER
        );
        """)



def insert_on_table_map_address_to_node(cursor, ip_address, node_id):
    cursor.execute("INSERT INTO map_address_to_node (address, node_id) VALUES (" + ip_address + ", " + node_id + ");")

def insert_on_table_map_link_to_nodes(cursor, link_id, node_id_1, address_1, node_id_2, address_2, relationship):
    cursor.execute("INSERT INTO map_link_to_nodes (link_id, node_id_1, address_1, node_id_2, address_2, relationship) VALUES (" + link_id + ", " + node_id_1 + ", " + address_1 + ", " + node_id_2 + ", " + address_2 + ", " + relationship + ");")

def insert_on_table_map_node_to_asn(cursor, node_id, as_number):
    cursor.execute("INSERT INTO map_node_to_asn (node_id, as_number) VALUES (" + node_id + ", " + as_number + ");")



def match_address_from_table_map_address_to_node(cursor, ip_address):
    cursor.execute("SELECT * FROM map_address_to_node WHERE address = '" + ip_address + "';")
    return cursor.fetchall()

def match_node_id_from_table_map_address_to_node(cursor, node_id):
    cursor.execute("SELECT * FROM map_address_to_node WHERE node_id = '" + node_id + "';")
    return cursor.fetchall()



def match_link_id_from_table_map_link_to_nodes(cursor, link_id):
    cursor.execute("SELECT * FROM map_link_to_nodes WHERE link_id = '" + link_id + "';")
    return cursor.fetchall()

def match_node_id_from_table_map_link_to_nodes(cursor, node_id):
    cursor.execute("SELECT * FROM map_link_to_nodes WHERE node_id_1 = '" + node_id + "' OR node_id_2 = '" + node_id + "';")
    return cursor.fetchall()

def match_address_from_table_map_link_to_nodes(cursor, address):
    cursor.execute("SELECT * FROM map_link_to_nodes WHERE address_1 = '" + address + "' OR address_2 = '" + address + "';")
    return cursor.fetchall()



def match_node_id_from_table_map_node_to_asn(cursor, node_id):
    cursor.execute("SELECT * FROM map_node_to_asn WHERE node_id = '" + node_id + "';")
    return cursor.fetchall()

def match_asn_from_table_map_node_to_asn(cursor, as_number):
    cursor.execute("SELECT * FROM map_node_to_asn WHERE as_number = '" + as_number + "';")
    return cursor.fetchall()



def main():
    cnxn = connect_ip_version()
    cursor = cnxn.cursor()
    create_tables(cursor)
    cnxn.close()

main()