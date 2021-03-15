import networkx as nx

# Directed graph with no nodes or edges
def blank_network():
    return nx.DiGraph()

def neighborhood_diameter(graph):
    return nx.diameter(graph)

# returns node ID if graph alreeady contains a node for this address
# returns -1 if graph contains no entry for this address
def contains_address(graph, address):

    return False

# node_id - ID in CAIDA ITDK
# hostnames - list of hostnames used by this node
# addresses - list of addresses resolved to this node
def add_node(graph, node_id, host_names, addresses):
    return graph

# edges are directed
# rtts - list of rtt values discovered in traces. empty if not applicable
def add_edge(graph, node_id_1, node_id_2, link_num, rtts):

    # if no such edge already exists, add it to the graph
    if not graph.has_edge(node_id_1, node_id_2):

        # add edge without RTT data from a traceroute
        if not rtts:
            graph.add_edge(node_id_1, node_id_2, link_id=link_num)

        # add edge with RTT data from a traceroute
        else:
            graph.add_edge(node_id_1, node_id_2, link_id=link_num, rtt_list=rtts)

    # if edge already exists, just add the RTTs to the edge's rtt_list attribute
    # in non-multigraph NetworkX, adding an edge that already exists simply updates the edge's data
    else:
        old_rtt_list = rtt_list[(node_id_1, node_id_2)]
        new_rtt_list = old_rtt_list + rtts
        graph.add_edge(node_id_1, node_id_2,  link_id=link_num, rtt_list=new_rtt_list)


    return graph


def possible_paths(graph, node_id_1, node_id_2):
    return None


def serialize(graph, target_file):
    target = open(target_file)

    for line in nx.generate_graphml(graph, prettyprint=True):
        target.write(line)

    target.close()

    return None

def deserialize(file):
    return nx.read_graphml(file)