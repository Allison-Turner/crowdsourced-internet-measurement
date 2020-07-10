#!/usr/bin/python
import cim_util, os, subprocess, re

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
        self.hops = []
        self.ip_version = "IPv4"

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

def run_trace(ipv4):
    ptrace_log = open(cim_util.file, "a")
    if ipv4 is True:
        ptrace = subprocess.Popen(["/usr/sbin/paris-traceroute", "-4", "google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        ptrace = subprocess.Popen(["/usr/sbin/paris-traceroute", "-6", "google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out = ptrace.stdout.read()
    err = ptrace.stderr.read()

    ptrace_log.write("\nSTDOUT\n")
    ptrace_log.write("================================================================\n")
    ptrace_log.write(out)

    ptrace_log.write("\nSTDERR\n")
    ptrace_log.write("================================================================\n")
    ptrace_log.write(err)

    ptrace_log.close()

def trim_address(token):
    router_addr = token.replace(',','')
    router_addr = router_addr.replace('(', '')
    router_addr = router_addr.replace(')', '')
    return str(router_addr)

def parse_traces():
    # File Annotation Regular Expressions
    stdout = re.compile("STDOUT")
    stderr = re.compile("STDERR")
    divider = re.compile("((=)+)")
    whitespace = re.compile("\s")
    star = re.compile("\*")

    # Header Line and Fields Regular Expressions
    header = re.compile("\Atraceroute to (.)+")
    domain_name = re.compile("[a-zA-Z]+\.[com|org|edu|net]")
    header_num = re.compile("\d{1,5}")

    # Hop Fields Regular Expressions
    hop_num = re.compile("\d{1,3}")
    name = re.compile("(\w+[:|\.|-]*)+")
    time = re.compile("\d+\.\d+ms")
    # IPv4 and IPv6 address Regular Expressions (source: https://gist.github.com/mnordhoff/2213179 )
    ipv4_pattern = re.compile('^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
    ipv6_pattern = re.compile('^(?:(?:[0-9A-Fa-f]{1,4}:){6}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|::(?:[0-9A-Fa-f]{1,4}:){5}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,4}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){,6}[0-9A-Fa-f]{1,4})?::)$')


    # Track parsed/parsing traces and hops
    traces = []
    current_trace = -1
    current_hop = -1
    # Are we currently in an stderr section?
    err = False

    ptrace_log = open(cim_util.file, "r")

    for line in ptrace_log:
        if header.match(line):
            current_trace += 1
            current_hop = (-1)
            traces.append(Trace_Path())

            tokens = re.split("\s", line)

            for token in tokens:
                if domain_name.match(token):
                    traces[current_trace].set_dest_name(token)

                elif cim_util.ipv4_pattern.match(trim_address(token)):
                    traces[current_trace].set_ip_version("IPv4")
                    traces[current_trace].set_dest_addr(trim_address(token))

                elif cim_util.ipv6_pattern.match(trim_address(token)):
                    traces[current_trace].set_ip_version("IPv6")
                    traces[current_trace].set_dest_addr(trim_address(token))

                elif header_num.match(token):
                    if traces[current_trace].hops_max == 0:
                        traces[current_trace].set_hops_max(token)

                    elif traces[current_trace].pkt_size == 0:
                        traces[current_trace].set_packet_size(token)

        else:
            new_hop = False
            set_name = False
            tokens = re.split("\s", line)

            for token in tokens:
                if divider.match(token) or whitespace.match(token) or len(token) < 1:
                    continue

                elif stdout.match(token):
                    err = False

                elif stderr.match(token):
                    err = True

                elif err is True and not divider.match(token) and len(token) > 0:
                    print(token)

                else:
                    if new_hop is False:
                        new_hop = True
                        current_hop += 1
                        traces[current_trace].add_hop(Hop(current_hop + 1))

                    if time.match(token):
                        traces[current_trace].hops[current_hop].add_time(token)

                    elif cim_util.ipv4_pattern.match(trim_address(token)) or cim_util.ipv6_pattern.match(trim_address(token)):
                        traces[current_trace].hops[current_hop].set_hop_ip(token)

                    elif name.match(token) and len(token) > 3:
                        traces[current_trace].hops[current_hop].set_hop_name(token)
                        set_name = True

            if set_name is False and new_hop is True:
                node = traces[current_trace].hops[current_hop]
                node.set_hop_name(node.ip)


    ptrace_log.close()
    return traces

def match_nodes(trace):
    print("placeholder for node match to CAIDA data")
    if trace.ip_version == "IPv4":
        print("vfndjgb")
    elif trace.ip_version == "IPv6":
        print("udctgdcj")

def main():
    run_trace(True)
    run_trace(False)

    paths = parse_traces()
    for p in paths:
        print("================================================================\n")
        print(p.to_string() + "\n")

    for p in paths:
        match_nodes(p)

main()
