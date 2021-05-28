#!/usr/bin/python3

import cim_util, subprocess, re, pyodbc

class Hop:
    def __init__(self, hop_num):
        self.hop_count = hop_num
        self.ip = "*"
        self.name = "*"
        self.times = []

    def set_hop_ip(self, hop_ip):
        self.ip = trim_address(hop_ip)

    def set_hop_name(self, hop_name):
        self.name = hop_name

    def add_time(self, time):
        trimmed_time = time.replace("ms", "")
        self.times.append(trimmed_time)

    def to_string(self):
        print_string = "Hop Number: " + str(self.hop_count) + "\nName: " + str(self.name) + "\nAddress: " + str(self.ip) + "\nRound Trip Times:"
        t = 0
        while t < 3:
            print_string += " "
            if t > (len(self.times) - 1):
                print_string += "*"
            else:
                print_string += str(self.times[t])
            t += 1
        return print_string

class Trace_Path:
    def __init__(self):
        self.dest_name = ""
        self.dest_addr = ""
        self.hops_max = 0
        self.pkt_size = 0
        self.ip_version = "IPv4"
        self.hops = []

    def add_hop(self, hop):
        self.hops.insert(int(hop.hop_count), hop)

    def set_ip_version(self, ip_v):
        self.ip_version = ip_v

    def set_dest_name(self, name):
        self.dest_name = name

    def set_dest_addr(self, addr):
        self.dest_addr = addr

    def set_hops_max(self, max):
        self.hops_max = max

    def set_packet_size(self, size_bytes):
        self.pkt_size = size_bytes

    def to_string(self):
        print_string = "Destination Name: " + str(self.dest_name) + "\nIP Version:" + str(self.ip_version) + "\nDestination Address: " + str(self.dest_addr) + "\nMax Hops: " + str(self.hops_max) + "\nPacket Size: " + str(self.pkt_size)
        for hop in self.hops:
            print_string += "\n\n" + hop.to_string()
        return print_string



def trim_address(token):
    router_addr = token.replace(',','')
    router_addr = router_addr.replace('(', '')
    router_addr = router_addr.replace(')', '')
    return str(router_addr)



def parse_traces(trace_log=cim_util.s1_trace_log):
    # Track parsed/parsing traces and hops
    traces = []
    current_trace = -1
    current_hop = -1

    # Are we currently in an stderr section?
    err = False

    ptrace_log = open(trace_log, "r")

    for line in ptrace_log:

        # trace metadata header
        if cim_util.header.match(line):

            current_trace += 1
            current_hop = (-1)
            traces.append(Trace_Path())

            tokens = re.split("\s", line)

            for token in tokens:
                if cim_util.domain_name.match(token):
                    traces[current_trace].set_dest_name(token)

                elif cim_util.ipv4_pattern.match(trim_address(token)):
                    traces[current_trace].set_ip_version("IPv4")
                    traces[current_trace].set_dest_addr(trim_address(token))

                elif cim_util.ipv6_pattern.match(trim_address(token)):
                    traces[current_trace].set_ip_version("IPv6")
                    traces[current_trace].set_dest_addr(trim_address(token))

                elif cim_util.header_num.match(token):
                    if traces[current_trace].hops_max == 0:
                        traces[current_trace].set_hops_max(token)

                    elif traces[current_trace].pkt_size == 0:
                        traces[current_trace].set_packet_size(token)

        # trace hop or logging output section
        else:
            new_hop = False
            set_name = False
            tokens = re.split("\s", line)

            for token in tokens:
                # Divider, whitespace, or zero-length token --> ignore
                if cim_util.divider.match(token) or cim_util.whitespace.match(token) or len(token) < 1:
                    continue

                # STDOUT section starts --> ensure parser does not register following tokens as error output
                elif cim_util.stdout.match(token):
                    err = False

                # STDERR section starts --> ensure parser registers following tokens as error output
                elif cim_util.stderr.match(token):
                    err = True

                # print error output
                elif err is True and not cim_util.divider.match(token) and len(token) > 0:
                    print(token)

                # parsing hops
                else:
                    if new_hop is False:
                        new_hop = True
                        current_hop += 1
                        traces[current_trace].add_hop(Hop(current_hop + 1))

                    # RTT
                    if cim_util.time.match(token):
                        traces[current_trace].hops[current_hop].add_time(token)

                    # IP Address
                    elif cim_util.ipv4_pattern.match(trim_address(token)) or cim_util.ipv6_pattern.match(trim_address(token)):
                        traces[current_trace].hops[current_hop].set_hop_ip(token)

                    # Hostname
                    elif cim_util.name.match(token) and len(token) > 3:
                        traces[current_trace].hops[current_hop].set_hop_name(token)
                        set_name = True

            # if there is no separate hostname, the hostname is the IP address
            if set_name is False and new_hop is True:
                node = traces[current_trace].hops[current_hop]
                node.set_hop_name(node.ip)


    ptrace_log.close()

    return traces