#!/usr/bin/python3
import cim_util, subprocess, re, pyodbc, process_trace, cim_db_util, neighborhood_view

def run_trace(ipv4=True, trace_file=cim_util.s1_trace_log):
    ptrace_log = open(trace_file, "a")

    if ipv4 is True:
        ptrace = subprocess.Popen(["/usr/sbin/paris-traceroute", "-4", "--src-port=51000", "--dst-port=80", "google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        ptrace = subprocess.Popen(["/usr/sbin/paris-traceroute", "-6", "--src-port=51000", "--dst-port=80", "google.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out = ptrace.stdout.read()
    err = ptrace.stderr.read()

    ptrace_log.write("\nSTDOUT\n")
    ptrace_log.write("================================================================\n")
    ptrace_log.write(out)

    ptrace_log.write("\nSTDERR\n")
    ptrace_log.write("================================================================\n")
    ptrace_log.write(err)

    ptrace_log.close()



def match_nodes(trace, network_map, cursor, ipv4=True):

    for hop in trace.hops:
        ids = cim_db_util.match_address_from_table_map_address_to_node(cursor, hop.ip)

        if len(ids) > 1:
            print("More than one match")
            for n in ids:
                print(str(n.node_id))  

        elif len(ids) < 1:
            print("No matches")

        else:
            node_id = ids[0].node_id
            print("Single match:" + str(node_id))

            addresses = cim_db_util.match_node_id_from_table_map_address_to_node(cursor, node_id)

            neighborhood_view.add_node(network_map, node_id, hop.name, addresses) 

def main():
    run_trace()

    paths = process_trace.parse_traces()

    for p in paths:
        print("================================================================\n")
        print(p.to_string() + "\n")

    # for p in paths:
    #    match_nodes(p)

main()
