class Topology:
    vertices = []
    edges = []

    def __init__(self, is_ipv4=True):
        self.ipv4 = is_ipv4

    # Add a new node to the vertices list, keeping the list ordered by node ID
    def add_node(self, node):
        # fill in later
        print("vfehvf")

    # Add a new link to the edges list, keeping the list ordered by link ID
    def add_link(self, link):
        # fill in later
        print("affdrdvs")

class Node:
    aliases = []
    links = []
    as_owner = -1

    def __init__(self, nID=-1):
        aliases.append(Alias(addr))
        self.nodeID = nID

    def add_alias(self, alias):
        if self.nodeID != -1:
            self.aliases.append(Alias(alias))
        else:
            print("Cannot add an alias to a node without a node ID")

    # Add links at the node level but divide them by aliases if you can
    def add_link(self, link):
        self.links.append(link)

    def assign_AS_ownership(self, ASN):
        self.as_owner = ASN

class Alias:
    links = []

    def __init__(self, addr, T=False, D=False):
        self.address = addr
        self.transitHop = T
        self.destHop = D

    def add_link(self, linkID):
        print("add new link to node interface, ordering list by link ID")

class Link:
    def __init__(self, lID, n1, n2):
        self.linkID = lID
        self.node1 = n1
        self.node2 = n2
