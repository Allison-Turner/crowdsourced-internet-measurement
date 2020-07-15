#!/usr/bin/python3
import os, re
from time import strftime,localtime

# environment metadata
user = "allison-turner"
home = os.path.expanduser("~" + user)

# probe_and_overlay.py metadata
s1_trace_log = home + "/Desktop/" + "trace.log"

# build_map.py metadata
itdk_year = "2019"
itdk_month = "01"
itdk_day = "11"
itdk_folder_loc = home + "/Downloads/ITDK-" + itdk_year + "-" + itdk_month + "/"
compression_extension = ".bz2"

# IPv4 via midar-iffinder: .nodes + .links + .ifaces + .as + .geo
# IPv6 via speedtrap: .nodes + .links + .as + .geo
ipv4_topo_choice = "midar-iff"
ipv6_topo_choice = "speedtrap"
file_types = [".nodes", ".links", ".nodes.as", ".nodes.geo", ".ifaces"]

# Node & Link Regular Expressions
node_id_regex = "N([0-9]+)"
link_id_regex = "L([0-9]+)"

node_id_pattern = re.compile(node_id_regex)
link_id_pattern = re.compile(link_id_regex)

link_entry_prefix = re.compile("\Alink " + link_id_regex)
node_entry_prefix = re.compile("\Anode " + node_id_regex)

# IPv4 and IPv6 address Regular Expressions (source: https://gist.github.com/mnordhoff/2213179 )
ipv4_regex = '^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
ipv6_regex = '^(?:(?:[0-9A-Fa-f]{1,4}:){6}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|::(?:[0-9A-Fa-f]{1,4}:){5}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,4}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){,6}[0-9A-Fa-f]{1,4})?::)$'

ipv4_pattern = re.compile(ipv4_regex)
ipv6_pattern = re.compile(ipv6_regex)

# Regex for entries in .links files that take the format <Node ID>:<Address>
ipv4_link_end = re.compile(node_id_regex + ":" + ipv4_regex)
ipv6_link_end = re.compile(node_id_regex + ":" + ipv6_regex)

# Properties for pyodbc connection string
odbc_driver = "psqlOBDC"
db_server = "localhost"
db_name = "postgres"
db_user = "postgres"
db_pwd = "postgres"

def get_timestamp():
    return strftime("%H-%M-%S-%d-%m-%Y", localtime())
