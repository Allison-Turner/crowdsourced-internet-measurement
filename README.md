# Crowdsourced Measurements of Internet Traffic Manipulation #

## Stage 1 ##
We start stage 1 by downloading, decompressing, and parsing CAIDA data sets into usable topology data structures with build_map.py

| Option               | Required?          | Description |
| -------------------- | ------------------ | ----------- |
| [-h]                 | :x:                |
| -l FOLDER_LOC        | :heavy_check_mark: |
| [-y YEAR]            | :heavy_check_mark: |
| [-m MONTH]           | :heavy_check_mark: |
| [-a DAY]             | :heavy_check_mark: |
| [-e COMPRESSION_EXT] | :x:                |
| [-x EXTRACT_FILES]   | :x:                |
| [-w DOWNLOAD_FILES]  | :x:                |

```
python build_map.py -l $HOME/Downloads/ITDK-2019-01/ -w True
```

## CAIDA Macroscopic Internet Topology Data Kit (ITDK) ##

### Notes ###
When you download the files, they're all compressed in bz2 format. The data server can't establish HTTPS connections.

### Results by Suite ###
Topology core is given by .nodes and .links. Node metadata is given in .as and .geo. .ifaces attempts to reconstruct node interfaces based on alias resolution.

We'll be using IPv4 Router Topology A and the IPv6 Router Topology. We choose IPv4 A over B to favor accuracy.

* IPv4 Router Topology A (accurate alias resolution):
  * midar-iffinder.nodes
  * midar-iffinder.links
  * midar-iffinder.nodes.as
  * midar-iffinder.nodes.geo
  * midar-iffinder.ifaces


* IPv4 Router Topology B (comprehensive alias resolution):
  * midar-iffinder-kapar.nodes
  * midar-iffinder-kapar.links
  * midar-iffinder-kapar.nodes.as
  * midar-iffinder-kapar.nodes.geo
  * midar-iffinder-kapar.ifaces


* IPv6 Router Topology (speedtrap IPv6 alias resolution):
  * speedtrap.nodes
  * speedtrap.links
  * speedtrap.nodes.as
  * speedtrap.nodes.geo

### File Format Notes ###

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
