#!/usr/bin/python3
class Topology:

    def __init__(self, is_ipv4=True):
        self.ipv4 = is_ipv4
        self.vertices = []
        self.edges = []

    # Add a new node to the vertices list, keeping the list ordered by node ID
    def add_node(self, node):
        if len(self.vertices) == 0:
            self.vertices.append(node)
        else:
            index = 0
            inserted = False
            while index < len(self.vertices) and not inserted:
                if node.node_id > self.vertices[index].node_id:
                    self.vertices.insert(index, node)
                    inserted = True

                index += 1

            if not(inserted):
                self.vertices.append(node)

    # Add a new link to the edges list, keeping the list ordered by link ID
    def add_link(self, link):
        edges.append(link)
        edges.sort(key=link_sort)

class Node:
    def __init__(self, nID=-1, as=-1):
        self.node_id = nID
        self.aliases = []
        self.links = []
        self.as_owner = as

    def add_alias(self, alias):
        if self.node_id != -1:
            self.aliases.append(Alias(alias))
        else:
            print("Cannot add an alias to a node without a node ID")

    # Add links at the node level but divide them by aliases if you can
    def add_link(self, link):
        self.links.append(link)

    def assign_AS_ownership(self, ASN):
        self.as_owner = ASN

class Alias:
    def __init__(self, addr, T=False, D=False):
        self.links = []
        self.address = addr
        self.transitHop = T
        self.destHop = D

    def add_link(self, link_id):
        print("add new link to node interface, ordering list by link ID")

class Link:
    def __init__(self, lID, n1, n2):
        self.link_id = lID
        self.node1 = n1
        self.node2 = n2
