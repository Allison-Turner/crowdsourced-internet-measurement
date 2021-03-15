#!/usr/bin/python3

import os, cim_util, subprocess, datetime, re, pyodbc
from argparse import ArgumentParser

timestamp = cim_util.get_timestamp()

# Set up command line argument parser
parser = ArgumentParser(description="A program to parse CAIDA ITDK files into useful topology data structures")
parser.add_argument("-l", "--location", dest="folder_loc", default=cim_util.itdk_folder_loc, help="location of ITDK data archive folder, up to and including the folder name")
parser.add_argument("-y", "--year", dest="year", default=cim_util.itdk_year, help="year of ITDK version")
parser.add_argument("-m", "--month", dest="month", default=cim_util.itdk_month, help="month of ITDK version")
parser.add_argument("-d", "--day", dest="day", default=cim_util.itdk_day, help="day of ITDK version")
parser.add_argument("-e", "--compression_ext", dest="compression_ext", default=cim_util.compression_extension, help="compression file extension for ITDK data archive files")
parser.add_argument("-x", "--extract_files", dest="extract_files", default=False, help="Whether the data archive files need to be decompressed")
parser.add_argument("-w", "--download_files", dest="download_files", default=False, help="Whether to download the data files from CAIDA's data server")


def download_files(ipv4, ipv6, extension, location, day, month, year):
    if not os.path.exists(location):
        os.mkdir(location)

    download_log = open(location + "download" + timestamp + ".log", "a+")

    if ipv4:
        # Download all files to listed folder location
        for file in cim_util.file_types:
            download_log.write("Downloading " + cim_util.ipv4_topo_choice + file + extension + "\n")
            download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", location, cim_util.ipv4_itdk_url + year + "-" + month + "/" + cim_util.ipv4_topo_choice + file + extension ])
            download_cmd.communicate()
            cim_util.log_cmd_results(download_cmd, download_log)

    if ipv6:
        for file in cim_util.file_types:
            if file != ".ifaces":
                download_log.write("Downloading " + cim_util.ipv6_topo_choice + file + extension + "\n")
                download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", location, cim_util.ipv4_itdk_url + year + "-" + month + "/" + cim_util.ipv6_topo_choice + file + extension ])
                download_cmd.communicate()
                cim_util.log_cmd_results(download_cmd, download_log)

    if ipv4:
        download_log.write("Downloading itdk-run-" + year + month + day + "-dns-names.txt" + extension + "\n")
        download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", location, cim_util.ipv4_itdk_url + year + "-" + month + "/" + "itdk-run-" + year + month + day + "-dns-names.txt" + extension ])
        download_cmd.communicate()
        cim_util.log_cmd_results(download_cmd, download_log)

        download_log.write("Downloading itdk-run-" + year + month + day + ".addrs" + extension + "\n")
        download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", location, cim_util.ipv4_itdk_url + year + "-" + month + "/" + "itdk-run-" + year + month + day + ".addrs" + extension ])
        download_cmd.communicate()
        cim_util.log_cmd_results(download_cmd, download_log)

    download_log.close()


def decompress(ipv4, ipv6, extension, location):
    # Prep log file
    decompress_log = open(location + "decompression"+ timestamp + ".log", "a")

    #decompress archive files
    if extension == ".bz2":
        if ipv4:
            # Decompress IPv4 archives
            decompress_log.write("IPv4 Archives\n")
            for file in cim_util.file_types:
                decompress_log.write("Decompressing " + location + cim_util.ipv4_topo_choice + file + ".bz2\n")
                decompress_cmd = subprocess.Popen(["/usr/bin/bzip2", "-d", location + cim_util.ipv4_topo_choice + file + ".bz2"])
                decompress_cmd.communicate()
                cim_util.log_cmd_results(decompress_cmd, decompress_log)

        if ipv6:
            # Decompress IPv6 archives (no ifaces file for this topology)
            decompress_log.write("IPv6 Archives\n")
            for file in cim_util.file_types:
                if file != ".ifaces":
                    decompress_log.write("Decompressing " + location + cim_util.ipv6_topo_choice + file + ".bz2\n")
                    decompress_cmd = subprocess.Popen(["/usr/bin/bzip2", "-d", location + cim_util.ipv6_topo_choice + file + ".bz2"])
                    decompress_cmd.communicate()
                    cim_util.log_cmd_results(decompress_cmd, decompress_log)

    decompress_log.close()


def read_in_nodes(ip_version, cursor):
    # Open nodes file to begin extracting node objects
    if ip_version == "IPv4":
        nodes_file = open(args.folder_loc + cim_util.ipv4_topo_choice + cim_util.file_types[0], "r")

    elif ip_version == "IPv6":
        nodes_file = open(args.folder_loc + cim_util.ipv6_topo_choice + cim_util.file_types[0], "r")

    found = 0

    for line in nodes_file:
        # Read in node objects
        prefix = cim_util.node_entry_prefix.search(line)
        if prefix is not None:
            # Parse node ID
            n_ID = cim_util.node_id_pattern.search(line).group()[1:]

            # Split entry by whitespace
            tokens = re.split("\s", line)

            # Add node aliases
            for token in tokens:
                if ip_version == "IPv4" and cim_util.ipv4_pattern.match(token):
                    cursor.execute("INSERT INTO ipv4_topology.map_address_to_node (address, node_id) VALUES (?, ?);", (token, n_ID))

                elif ip_version == "IPv6" and cim_util.ipv6_pattern.match(token):
                    cursor.execute("INSERT INTO ipv6_topology.map_address_to_node (address, node_id) VALUES (?, ?);", (token, n_ID))

            # Save all new entries to database from this line
            cursor.commit()

            # Stop parsing after 100 records for development purposes
            found += 1
            if found > 100:
                break

    nodes_file.close()


def read_in_links(ip_version, cursor):
    if ip_version == "IPv4":
        links_file = open(args.folder_loc + cim_util.ipv4_topo_choice + cim_util.file_types[1], "r")

    elif ip_version == "IPv6":
        links_file = open(args.folder_loc + cim_util.ipv6_topo_choice + cim_util.file_types[1], "r")

    for line in links_file:
        prefix = cim_util.link_entry_prefix.search(line)

        if prefix is not None:
            link_ID = cim_util.link_id_pattern.search(line).group()[1:]
            n1_id = None
            n1_addr = None

            tokens = re.split("\s", line)
            for token in tokens:
                if cim_util.node_id_pattern.match(token):
                    print()

                elif ip_version == "IPv4":
                    if cim_util.ipv4_link_end.match(token):
                        if n1_id is None:
                            print()

                        else:
                            sides = re.split(":", token)
                            n_ID = sides[0]
                            addr = sides[1]
                            print()

                    elif cim_util.ipv4_pattern.match(token):
                        print()

                elif ip_version == "IPv6":
                    if cim_util.ipv6_link_end.match(token):
                        if n1_id is None:
                            print()
                        else:
                            # can't split on : because that's part of IPv6 addresses
                            n_ID = cim_util.node_id_pattern.search(token)
                            addr = token[n_ID.end() + 2:]
                            ID = n_ID.group()
                            cursor.execute("INSERT INTO ipv6_topology.map_link_to_nodes (link_id, node_id_1, address_1, node_id_2, address_2) VALUES (?, );", (link_ID, ))
                            print()

                    elif cim_util.ipv6_pattern.match(token):
                        print()

    links_file.close()

def clean_db(cursor):
    cursor.execute()

def main():
    args = parser.parse_args()

    # Download data archives
    if args.download_files:
        print("Downloading files from CAIDA data server")
        download_files(args.compression_ext, args.folder_loc, args.day, args.month, args.year)

    #Extract files
    if args.extract_files or args.download_files:
        print("Decompressing files")
        decompress(args.compression_ext, args.folder_loc)

    # Connect to database
    cnxn = pyodbc.connect("DRIVER={" + cim_util.odbc_driver + "};SERVER=" + cim_util.db_server + ";DATABASE=" + cim_util.db_name + ";UID=" + cim_util.db_user + ";PWD=" + cim_util.db_pwd)
    cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    cnxn.setencoding(encoding='utf-8')
    cursor = cnxn.cursor()

    # Create schemas and tables
    cursor.execute("CREATE SCHEMA IF NOT EXISTS ipv4_topology AUTHORIZATION "+ cim_util.db_user +
    """
      CREATE TABLE map_address_to_node(
        address inet,
        node_id integer
      )
      CREATE TABLE map_link_to_nodes(
        link_id integer,
        node_id_1 integer,
        address_1 inet, -- optional
        node_id_2 integer,
        address_2 inet, -- optional
        relationship text
      )
      CREATE TABLE map_node_to_asn(
        node_id integer,
        as_number integer
      );

    CREATE SCHEMA IF NOT EXISTS ipv6_topology AUTHORIZATION postgres
      CREATE TABLE map_address_to_node(
        address inet,
        node_id integer
      )
      CREATE TABLE map_link_to_nodes(
        link_id integer,
        node_id_1 integer,
        address_1 inet, -- optional
        node_id_2 integer,
        address_2 inet, -- optional
        relationship text
      )
      CREATE TABLE map_node_to_asn(
        node_id integer,
        as_number integer
      );
    """);

    # Read in IPv4 nodes
    read_in_nodes("IPv4", cursor)

    # Read in IPv6 nodes
    # read_in_nodes("IPv6", cursor)

    # Read in IPv4 links
    read_in_links("IPv4", cursor)

    # Read in IPv6 links
    # read_in_links("IPv6", cursor)

    cnxn.close()

main()
