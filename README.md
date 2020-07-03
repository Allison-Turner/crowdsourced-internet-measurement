# Crowdsourced Measurements of Internet Traffic Manipulation #

## Stage 1 ##
Stage 1 aims to situate the tester on a global map of internet topology. We draw this map from CAIDA's data sets generated by its Ark monitor network, especially the Macroscopic Internet Topology Data Kit (ITDK).
<br>
We begin by downloading, decompressing, and parsing CAIDA data sets into usable topology data structures with build_map.py. The data structures are filled with nodes first, links by interface next when possible, and all remaining links last. We annotate the map with autonomous system metadata selectively during data analysis to reduce the storage and processing loads. Note that we'll only build this map on a lab computer. It's unnecessary to perform the large and costly process of building the map data structures from the CAIDA data sets on a tester's computer.
<br>
Below are the possible command line arguments for running build_map.py

| Option               | Required?          | Description                                          | Default Value |
| -------------------- | ------------------ | ---------------------------------------------------- | ------------- |
| [-h]                 | :x:                | see all argument options                             |               |
| -l FOLDER_LOC        | :heavy_check_mark: | folder path to archive files                         |               |
| [-y YEAR]            | :heavy_check_mark: | year of CAIDA measurements, in 20xx form             | 2019          |
| [-m MONTH]           | :heavy_check_mark: | month of CAIDA measurements, in 01 or 12 form        | 01            |
| [-a DAY]             | :heavy_check_mark: | day of CAIDA measurements, in 03 or 22 form          | 11            |
| [-e COMPRESSION_EXT] | :x:                | compression file extension                           | .bz2          |
| [-x EXTRACT_FILES]   | :x:                | whether to decompress archive files                  | False         |
| [-w DOWNLOAD_FILES]  | :x:                | whether to download data archives from CAIDA servers | False         |

Example command:
```
python build_map.py -l $HOME/Downloads/ITDK-2019-01/ -w True
```

## Stage 2 ##

## Stage 3 ##

## CAIDA Macroscopic Internet Topology Data Kit (ITDK) ##

### Notes ###
* When you download the files, they're all compressed in bz2 format.
* The data server can't establish HTTPS connections.

### Result Suites ###
We'll be using IPv4 Router Topology A and the IPv6 Router Topology. Topology B uses a more comprehensive alias resolution tactic that can also result in false positives. We choose Topology A over B to favor accuracy.

* IPv4 Router Topology A (accurate alias resolution):
  * midar-iff.nodes
  * midar-iff.links
  * midar-iff.nodes.as
  * midar-iff.nodes.geo
  * midar-iff.ifaces


* IPv4 Router Topology B (comprehensive alias resolution):
  * kapar-midar-iff.nodes
  * kapar-midar-iff.links
  * kapar-midar-iff.nodes.as
  * kapar-midar-iff.nodes.geo
  * kapar-midar-iff.ifaces


* IPv6 Router Topology (speedtrap IPv6 alias resolution):
  * speedtrap.nodes
  * speedtrap.links
  * speedtrap.nodes.as
  * speedtrap.nodes.geo

### File Format Notes ###
Topology core is given by .nodes and .links. Node metadata is given in .as and .geo. .ifaces attempts to reconstruct node interfaces based on alias resolution.

* itdk-run-<date>.addrs contains the target addresses used for the ITDK run

* itdk-run-<date>-dns-names.txt contains the DNS entries for every address used or discovered in measurement
  * <timestamp>    <IP-address>    <DNS-name>

* .nodes
  * Format: node <node_id>:   <i1>   <i2>   ...   <in>
  * Example: node N33382:  4.71.46.6 192.8.96.6 0.4.233.32

* .links
  * link <link_id>:   <N1>:i1   <N2>:i2   [<N3>:[i3] .. [<Nm>:[im]]

* .nodes.as
  * node.AS   <node_id>   <AS>   <method>

* .nodes.geo
  * node.geo   <node_id>: <continent> <country> <region> <city> <latitude> <longitude>

* .ifaces
  * <address> [<node_id>] [<link_id>] [T] [D]
