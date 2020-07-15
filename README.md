# Crowdsourced Measurements of Internet Traffic Manipulation #

## Stage 1 ##
Stage 1 aims to situate the tester on a global map of internet topology. We draw this map from CAIDA's data sets generated by its Ark monitor network, especially the router-level Macroscopic Internet Topology Data Kit (ITDK). We parse these data sets into a relational database so we can query IP addresses discovered by Paris traceroute for their associated ITDK node ID. Matching nodes from several traces in this manner allows us to place the machine in question on the map.

### [CAIDA Macroscopic Internet Topology Data Kit (ITDK)](https://www.caida.org/data/internet-topology-data-kit/) ###

#### Result Suites ####
We'll be using IPv4 Router Topology A and the IPv6 Router Topology. Topology B uses a more comprehensive alias resolution tactic that can also result in false positives. We choose Topology A over B to favor accuracy.

<details>
<summary> IPv4 Router Topology A (accurate alias resolution) </summary>
<ul>
 <li> midar-iff.nodes </li>
 <li> midar-iff.links </li>
 <li> midar-iff.nodes.as </li>
 <li> midar-iff.nodes.geo </li>
 <li> midar-iff.ifaces </li>
</ul>
</details>

<details>
<summary> IPv4 Router Topology B (comprehensive alias resolution) </summary>
 <ul>
  <li> kapar-midar-iff.nodes </li>
  <li> kapar-midar-iff.links </li>
  <li> kapar-midar-iff.nodes.as </li>
  <li> kapar-midar-iff.nodes.geo </li>
  <li> kapar-midar-iff.ifaces </li>
</details>

<details>
<summary> IPv6 Router Topology (speedtrap IPv6 alias resolution) </summary>
 <ul>
  <li> speedtrap.nodes </li>
  <li> speedtrap.links </li>
  <li> speedtrap.nodes.as </li>
  <li> speedtrap.nodes.geo </li>
  </ul>
</details>

#### File Formats ####
Topology core is given by .nodes and .links. Node metadata is given in .as and .geo. .ifaces attempts to reconstruct node interfaces based on alias resolution.

<details>
<summary> itdk-run-[date].addrs </summary>
 <p>contains the target addresses used by Ark monitors for the ITDK run </p>
</details>

<details>
<summary> itdk-run-[date]-dns-names.txt </summary>
 <p> Contains the DNS entries for every address used or discovered in measurement </p>
 <p> Format: <code> [timestamp]    [IP-address]    [DNS-name] </code> </p>
</details>

<details>
 <summary> .nodes </summary>
  <p> Format: <code> node [node_id]:   [i1]   [i2]   ...   [in] </code> </p>
  <p> Example: <code> node N33382:  4.71.46.6 192.8.96.6 0.4.233.32 </code> </p>
</details>

<details>
 <summary> .links </summary>
 <p> Format: <code> link [link_id]:   [N1]:i1   [N2]:i2   [[N3]:[i3] .. [[Nm]:[im]] </code> </p>
 <p> Example: <code> link L104:  N242484:211.79.48.158 N1847:211.79.48.157 N5849773 </code> </p>
</details>

<details>
 <summary> .nodes.as </summary>
 <p> Format: <code> node.AS   [node_id]   [AS]   [method] </code> </p>
 <p> Example: <code> node.AS N39 17645 election </code> </p>
</details>

<details>
 <summary> .nodes.geo </summary>
 <p> Format: <code> node.geo   [node_id]: [continent] [country] [region] [city] [latitude] [longitude] </code> </p>
 <p> Example: <code> node.geo N15:  ***  US  HI  Honolulu  21.3267  -157.8167 </code> </p>
</details>

<details>
 <summary> .ifaces </summary>
 <p> Format: <code> [address] [node_id] [link_id] [T] [D] </code> </p>
 <p> Example: <code> 1.0.174.107 N34980480 D </code> </p>
 <p> Example: <code> 1.0.101.6 N18137917 L537067 T </code> </p>
 <p> Example: <code> 1.28.124.57 N45020 </code> </p>
 <p> Example: <code> 11.3.4.2 N18137965 L537125 T D </code> </p>
 <p> Example: <code> 1.0.175.90 </code> </p>
</details>


### build_map.py ###
This file is reponsible for downloading, decompressing, and parsing CAIDA ITDK data files and then populating a database with the data.
<br><br>
Note that we'll only build this map on a lab computer. It's unnecessary to perform the large and costly process of building the map data structures from the CAIDA data sets on a tester's computer. Also note that we reserve annotation of the topology with metadata like AS number for the analysis stage, so that we can make selective use of the data to mitigate the size of the database.

<details>
 <summary> Requirements </summary>
 <ul>
  <li> cim_util </li>
  <li> <a href="https://github.com/mkleehammer/pyodbc/wiki">pyodbc</a> Python library </li>
  <li> <a href="https://docs.python.org/3/library/subprocess.html">subprocess</a> Python library </li>
  <li> <a href="https://docs.python.org/3/library/re.html">re</a> Python library </li>
  <li> <a href="https://docs.python.org/3/library/argparse.html">argparse</a> Python library </li>
  <li> <a href="https://www.gnu.org/software/wget/">wget</a> tool
    <ul>
      <li> assumes installation to usr/bin/wget </li>
    </ul>
  </li>
  <li> <a href="http://www.bzip.org/">bzip2</a> tool
  <ul>
    <li> assumes installation to usr/bin/bzip2 </li>
  </ul>
  </li>
  <li> internet connection </li>
 </ul>
</details>

<details>
<summary> download_files(extension, location, day, month, year) </summary>
<p> wgets all of the files we need of a particular ITDK release from CAIDA's file servers. The release is defined by the day, month, and year, which are given as arguments. The file extension is written as a variable to ensure flexibility, but it's usually .bz2. Creates a log from wget's stdout and stderr in case of download issues. </p>
<p> Note that this function requires an internet connection. </p>
</details>

<details>
<summary> decompress(extension, location) </summary>
<p> Decompresses data archives, usually in .bz2 format. Creates a log from bzip2's stdout and stderr in case of problems unzipping the files. </p>
</details>

<details>
<summary> read_in_nodes(ip_version, cursor) </summary>
<p> Opens the .nodes file from the ITDK release specified. Assumes that the file has already been downloaded and decompressed in the specified folder location. Reads the file line by line. When it encounters a line of the node entry format, inserts each IP address + node ID pair into the appropriate map_address_to_node table according to IP version. Commits after every matching line. </p>
</details>

<details>
<summary> read_in_links(ip_version, cursor) </summary>
<p> Opens the .links file from the ITDK release specified. Assumes that the file has already been downloaded and decompressed in the specified folder location. Reads the file line by line. When it encounters a line of the link entry format inserts each (link ID, node ID 1, node interface address 1, node ID 2, node interface address 2) tuple into the appropriate map_link_to_nodes table according to IP version. Commits after every matching line. </p>
</details>

You can run build_map.py without any command line arguments to use the values listed in cim_util.py and bypass file download and extraction, or you can use the following command line arguments to modify the run.

| Option               | Description                                          | Default Value                 |
| -------------------- | ---------------------------------------------------- | ----------------------------- |
| [-h]                 | see all argument options                             |                               |
| [-l FOLDER_LOC]      | folder path to archive files                         | $HOME/Downloads/ITDK-2019-01/ |
| [-y YEAR]            | year of CAIDA measurements, in 20xx form             | 2019                          |
| [-m MONTH]           | month of CAIDA measurements, in 01 or 12 form        | 01                            |
| [-d DAY]             | day of CAIDA measurements, in 03 or 22 form          | 11                            |
| [-e COMPRESSION_EXT] | compression file extension                           | .bz2                          |
| [-x EXTRACT_FILES]   | whether to decompress archive files                  | False                         |
| [-w DOWNLOAD_FILES]  | whether to download data archives from CAIDA servers | False                         |

Example command:
```
python build_map.py -l $HOME/Downloads/ITDK-2019-01/ -w True
```

### probe_and_overlay.py ###

<details>
 <summary> Requirements </summary>
 <ul>
 <li> cim_util </li>
 <li> <a href="https://docs.python.org/3/library/subprocess.html">subprocess</a> Python library </li>
 <li> <a href="https://docs.python.org/3/library/re.html">re</a> Python library </li>
 <li> <a href="https://paris-traceroute.net/">paris-traceroute</a> tool
    <ul>
     <li> needs root access </li>
    </ul>
  </li>
  <li> <a href="https://github.com/mkleehammer/pyodbc/wiki">pyodbc</a> Python library </li>
  <li> internet connection </li>
 </ul>
</details>

<details>
<summary> Hop </summary>
<p>[Object Class]</p>
<ul>
<li> hop_count [Integer]: number of network hops away from the source. </li>
<li> ip [String]: IPv4 or IPv6 address of the network node discovered in this hop. * if blank. </li>
<li> name [String]: name of network node. could be same as IP address. * if blank. </li>
<li> times [List of Floats]: round-trip times of all successful probe packet and responses for this hop. * if blank. all probes use a set of three packets for each hop. </li>
</ul>
</details>

<details>
<summary> Trace_Path </summary>
<p> [Object Class] </p>
<p> This class stores all of the properties of a paris-traceroute output </p>
<ul>
  <li>
    Trace Metadata
    <ul>
      <li> dest_name [String]: domain name of trace destination </li>
      <li> dest_addr [String]: IPv4 or IPv6 address of trace destination </li>
      <li> hops_max [Integer]: maximum TTL of traceroute packets </li>
      <li> pkt_size [Integer]: size of trace packets in bytes </li>
      <li> ip_version [String]: "IPv4" or "IPv6" to mark which format Hop addresses are in </li>
    </ul>
  </li>
  <li> Hops [List of Hop Objects]: all nodes discovered on the route to the targeted domain. </li>
</ul>
</details>

<details>
<summary> run_trace(ipv4) </summary>
<p> Runs a paris-traceroute and directs all stdout and stderr to the file defined by cim_util.s1_trace_log. Adds a -4 or -6 flag to force IPv4 or IPv6 according to the boolean parameter. </p>
<p> Note that this function requires an internet connection. </p>
</details>

<details>
<summary> trim_address(token) </summary>
<p> Removes parentheses and commas from parse tokens that may be IP addresses so that parse_traces() can accurately match tokens. </p>
</details>

<details>
<summary> parse_traces() </summary>
<p> Opens and reads the s1_trace_log to parse Trace_Path objects. Returns a list of Trace_Path objects. Prints all contents of stderr. </p>
</details>

<details>
<summary> match_nodes(trace) </summary>
<p> For every Hop in the Trace_Path given by parameter, selects rows from the map_address_to_node table of the appropriate topology schema to match paris-traceroute measured nodes to ITDK nodes. </p>
</details>

### cim_util.py ###
Contains various utilities: globally useful variables, regular expressions, and functions. All other files are written to pull specific variables from this file.

<details>
 <summary> Requirements </summary>
 <ul>
 <li> <a href="https://docs.python.org/3/library/re.html">re</a> Python library </li>
 <li> <a href="https://docs.python.org/3/library/os.html">os</a> Python library </li>
 <li> <a href="https://docs.python.org/3/library/time.html">time</a> Python library </li>
 </ul>
</details>

<details>
 <summary> Environment Properties </summary>
 <ul>
 <li> General
    <ul>
      <li> user </li>
      <li> home </li>
    </ul>
  </li>

  <li> build_map.py
    <ul>
      <li> itdk_folder_loc </li>
      <li> itdk_year </li>
      <li> itdk_month </li>
      <li> itdk_day </li>
      <li> compression_extension </li>
    </ul>
  </li>

  <li> probe_and_overlay.py
    <ul>
      <li> s1_trace_log </li>
    </ul>
  </li>

 </ul>
</details>

<details>
 <summary> CAIDA ITDK File Specifications </summary>
 <ul>
  <li> file_types
   <ul>
    <li> .nodes </li>
    <li> .links </li>
    <li> .nodes.as </li>
    <li> .nodes.geo </li>
    <li> .ifaces </li>
   </ul>
  </li>
  <li> topo_choice
   <ul>
    <li> midar-iff or kapar-midar-iff for IPv4 </li>
    <li> speedtrap for IPv6 </li>
   </ul>
  </li>
 </ul>
</details>

<details>
 <summary> Regular Expressions </summary>
 <ul>
  <li> node_id_pattern </li>
  <li> node_entry_prefix </li>
  <li> link_id_pattern </li>
  <li> link_entry_prefix </li>
  <li> ipv4_pattern </li>
  <li> ipv6_pattern </li>
 </ul>
</details>

<details>
 <summary> ODBC Connection String Fields </summary>
 <ul>
  <li> odbc_driver </li>
  <li> db_server </li>
  <li> db_name </li>
  <li> db_user </li>
  <li> db_pwd
   <ul> <li> Obviously we can't store passwords in text variables. Later I'll add some quiet command line prompts for password entry. </li> </ul>
  </li>

<details>
<summary> get_timestamp() </summary>
<p> Returns a timestamp string to mark log files. Format: "[hour]-[minute]-[second]-[day]-[month]-[year]" </p>
</details>

### Topology Database ###

<details>
  <summary>ipv4_topology</summary>
  <p>[Schema]</p>
  <ul>
    <li> [Table] map_address_to_node
      <ul>
        <li> [Column, Type=inet] address </li>
        <li> [Column, Type=integer] node_id </li>
      </ul>
    </li>

    <li> [Table] map_link_to_nodes
    <ul>
      <li> [Column, Type=integer] link_id </li>
      <li> [Column, Type=integer] node_id_1 </li>
      <li> [Column, Type=inet] address_1 </li>
      <li> [Column, Type=integer] node_id_2 </li>
      <li> [Column, Type=inet] address_2 </li>
      <li> [Column, Type=text] relationship </li>
    </ul>
    </li>

    <li> [Table] map_node_to_asn
    <ul>
      <li> [Column, Type=integer] node_id </li>
      <li> [Column, Type=integer] as_number </li>
    </ul>
    </li>

  </ul>
</details>

<details>
  <summary>ipv6_topology</summary>
  <p>[Schema]</p>
  <ul>
    <li> [Table] map_address_to_node
      <ul>
        <li> [Column, Type=inet] address </li>
        <li> [Column, Type=integer] node_id </li>
      </ul>
    </li>

    <li> [Table] map_link_to_nodes
    <ul>
      <li> [Column, Type=integer] link_id </li>
      <li> [Column, Type=integer] node_id_1 </li>
      <li> [Column, Type=inet] address_1 </li>
      <li> [Column, Type=integer] node_id_2 </li>
      <li> [Column, Type=inet] address_2 </li>
      <li> [Column, Type=text] relationship </li>
    </ul>
    </li>

    <li> [Table] map_node_to_asn
    <ul>
      <li> [Column, Type=integer] node_id </li>
      <li> [Column, Type=integer] as_number </li>
    </ul>
    </li>

  </ul>
</details>

## Stage 2 ##
Forthcoming, will integrate [Ariel's work](https://github.com/TraverAriel/Network-Measurement)

## Stage 3 ##
Forthcoming, will integrate [Ariel's work](https://github.com/TraverAriel/Network-Measurement)
