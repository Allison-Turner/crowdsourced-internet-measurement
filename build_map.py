from argparse import ArgumentParser
from net_topology import Topology, Node, Alias, Link
import subprocess, datetime, re

from time import strftime,localtime
timestamp = strftime("%H-%M-%S-%d-%m-%Y", localtime())
# timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%H-%M-%S-%d-%m-%Y")

# IPv4 via midar-iffinder: .nodes + .links + .ifaces + .as + .geo
# IPv6 via speedtrap: .nodes + .links + .as + .geo
ipv4_topo_choice = "midar-iff"
ipv6_topo_choice = "speedtrap"
file_types = [".nodes", ".links", ".nodes.as", ".nodes.geo", ".ifaces"]

# Set up command line argument parser
parser = ArgumentParser(description="A program to parse CAIDA ITDK files into useful topology data structures")
parser.add_argument("-l", "--location", dest="folder_loc", required=True, help="location of ITDK data archive folder, up to and including the folder name")
parser.add_argument("-y", "--year", dest="year", default="2019", help="year of ITDK version")
parser.add_argument("-m", "--month", dest="month", default="01", help="month of ITDK version")
parser.add_argument("-a", "--day", dest="day", default="11", help="day of ITDK version")
parser.add_argument("-e", "--compression_ext", dest="compression_ext", default=".bz2", help="compression file extension for ITDK data archive files")
parser.add_argument("-x", "--extract_files", dest="extract_files", default=False, help="Whether the data archive files need to be decompressed")
parser.add_argument("-w", "--download_files", dest="download_files", default=False, help="Whether to download the data files from CAIDA's data server")

def download_files(extension, location, day, month, year):
    download_log = open(location + "download" + timestamp + ".log", "a")

    # Download all files to listed folder location
    for file in file_types:
        download_log.write("Downloading " + ipv4_topo_choice + file + extension + "\n")
        download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", location, "http://data.caida.org/datasets/topology/ark/ipv4/itdk/" + year + "-" + month + "/" + ipv4_topo_choice + file + extension ])
        download_cmd.communicate()
        download_log.write("\n")


    for file in file_types:
        if file != ".ifaces":
            download_log.write("Downloading " + ipv6_topo_choice + file + extension + "\n")
            download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", location, "http://data.caida.org/datasets/topology/ark/ipv4/itdk/" + year + "-" + month + "/" + ipv6_topo_choice + file + extension ])
            download_cmd.communicate()
            download_log.write("\n")


    download_log.write("Downloading itdk-run-" + year + month + day + "-dns-names.txt" + extension + "\n")
    download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", location, "http://data.caida.org/datasets/topology/ark/ipv4/itdk/" + year + "-" + month + "/" + "itdk-run-" + year + month + day + "-dns-names.txt" + extension ])
    download_cmd.communicate()
    download_log.write("\n")

    download_log.write("Downloading itdk-run-" + year + month + day + ".addrs" + extension + "\n")
    download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", location, "http://data.caida.org/datasets/topology/ark/ipv4/itdk/" + year + "-" + month + "/" + "itdk-run-" + year + month + day + ".addrs" + extension ])
    download_cmd.communicate()
    download_log.write("\n")

    download_log.close()

def decompress(extension, location):
    # Prep log file
    decompress_log = open(location + "decompression"+ timestamp + ".log", "a")

    #decompress archive files
    if extension == ".bz2":
        # Decompress IPv4 archives
        decompress_log.write("IPv4 Archives\n")
        for file in file_types:
            decompress_log.write("Decompressing " + location + ipv4_topo_choice + file + ".bz2\n")
            decompress_cmd = subprocess.Popen(["/usr/bin/bzip2", "-d", location + ipv4_topo_choice + file + ".bz2"])
            decompress_cmd.communicate()

            decompress_log.write("Return Code: " + str(decompress_cmd.returncode) + "\n")

            decompress_log.write("STDOUT\n")
            decompress_log.write("==================================================\n")
            decompress_log.write(str(decompress_cmd.stdout) + "\n")

            decompress_log.write("STDERR\n")
            decompress_log.write("==================================================\n")
            decompress_log.write(str(decompress_cmd.stderr) + "\n")

        # Decompress IPv6 archives (no ifaces file for this topology)
        decompress_log.write("IPv6 Archives\n")
        for file in file_types:
            if file != ".ifaces":
                decompress_log.write("Decompressing " + location + ipv6_topo_choice + file + ".bz2\n")
                decompress_cmd = subprocess.Popen(["/usr/bin/bzip2", "-d", location + ipv6_topo_choice + file + ".bz2"])
                decompress_cmd.communicate()

                decompress_log.write("Return Code: " + str(decompress_cmd.returncode) + "\n")

                decompress_log.write("STDOUT\n")
                decompress_log.write("==================================================\n")
                decompress_log.write(str(decompress_cmd.stdout) + "\n")

                decompress_log.write("STDERR\n")
                decompress_log.write("==================================================\n")
                decompress_log.write(str(decompress_cmd.stderr) + "\n")

    decompress_log.close()


def main():
    args = parser.parse_args()

    # Initialize data structures
    ipv4_net = Topology()
    ipv6_net = Topology()

    # Download data archives
    if args.download_files:
        print("Downloading files from CAIDA data server")
        download_files(args.compression_ext, args.folder_loc, args.day, args.month, args.year)

    #Extract files
    if args.extract_files or args.download_files:
        print("Decompressing files")
        decompress(args.compression_ext, args.folder_loc)

    # Open IPv4 nodes file to begin extracting node objects
    ipv4_nodes = open(args.folder_loc + ipv4_topo_choice + file_types[0], "r")

    found = 0

    print("Parsing .nodes file to add vertices")
    for line in ipv4_nodes:
        # read in node objects
        prefix = re.search("\Anode N([0-9]+)", line)
        if prefix != None:
            # print("Current line: " + line)

            # Parse node ID
            id_start = prefix.group().index("N")
            n_ID = prefix.group()[(id_start + 1):]
            node = Node(n_ID)

            # Split entry by whitespace
            tokens = re.split("\s", line)

            # Add any token without a letter in it as an alias
            for token in tokens:
                containLetters = re.findall("[a-zA-Z]", token)
                if len(containLetters) < 1 and len(token) > 0:
                    node.add_alias(token)
                    # print("New alias for node " + n_ID + " at " + token)

            ipv4_net.add_node(node)

            print(node.node_id + " added")
            found += 1
            if found > 100:
                break

    ipv4_nodes.close()

    # print("Found " + len(ipv4_net.vertices) + " nodes.")
    for n in ipv4_net.vertices:
        print("Node " + n.node_id + " has " + str(len(n.aliases)) + " aliases.")
        print("\n")

    # ipv4_ifaces = open(args.folder_loc + ipv4_topo_choice + file_types[4], "r")

    # for line in ipv4_ifaces:
        # get iface entries

    # ipv4_ifaces.close()

main()
