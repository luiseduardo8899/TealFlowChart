from os.path import isfile, join
import os
import sys
import re
import glob
import graphviz
from graphviz import Digraph



alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','a1','b1','c1','d1','e1','f1','g1','h1','i1','j1','k1','l1','m1','n1','o1','p1','q1','r1','s1','t1','u1','v1','w1','x1','y1','z1'] #52 branches allowed so far


#Adda subgraph for each 
def add_subgraph(g, subgraph_name, subedges): 
    with g.subgraph(name=subgraph_name) as c:
        c.attr(style='filled', color='lightgrey')
        c.node_attr.update(style='filled', color='white')
        c.edges(subedges) #[('a', 'b'), ('c', 'd'), ('b', 'e')])
        c.attr(label=subgraph_name)

def remove_comment(text):
    code = text
    comment = None
    if ('//' in text): #remove comment part for now
        #print(line)
        ix = text.find("//")
        comment = text[ix:]
        code = text[:ix]
    return code, comment


# detect branch or subbranch
def detected_subranch(line):
    code, comment = remove_comment(line)
    if (":" in code): #check if it is a branch
        return 1

def branch_name_get_node(branch_name, branches):
    match_node = None

    for node, name in branches:
        if name == branch_name:
            match_node = node
    return match_node

def get_branch_name(line):
    name = None
    code, comment = remove_comment(line)
    if (":" in code): #check if it is a branch
        if(code[0] != " "): #Major branch
            print(code)
            name = code.replace(":", "")
            name = name.strip()
        else: # sub branch
            name = code.replace(":", "")
            name = name.strip()
    return name

def generate_main_branch_graph(teal_file):
    debug = 0 #TODO make programmable or get from command line
    gra = Digraph()
    branches = []
    branches.append([alphabet[0], "MAIN_PROGRAM"])

    with open(teal_file, 'r') as tf:
        ix = 1

        #First pass: define the main branches available -> define as edge nodes
        for line in tf:
            code, comment = remove_comment(line)
            if (":" in code): #check if it is a branch
                if(code[0] != " "): #Major branch
                    print(code)
                    name = code.replace(":", "")
                    name = name.strip()
                    gra.node(alphabet[ix], name)
                    #add_subgraph(gra, name)
                    branches.append([alphabet[ix], name]) #save all node names
                    ix +=1
                else: # sub branch
                    print("subbranch: ", code)
                    name = code.replace(":", "")
                    name = name.strip()
                    gra.node(alphabet[ix], name)
                    branches.append([alphabet[ix], name]) #save all node names


    with open(teal_file, 'r') as tf:
        ix = 0
        #Second pass define jumps between branches
        all_edges = []
        from_edge = alphabet[0]
        to_edge = None

        for line in tf:
            code, comment = remove_comment(line)

            if detected_subranch(code):
                name = get_branch_name(code)
                print("FROM BRANCH:", name)
                from_edge = branch_name_get_node(name, branches)
                print("FROM EDGE:", from_edge)

            if ('b ' in code): #always branch
                print(code)
                name = code.replace("b ", "")
                name = name.strip()
                to_edge = branch_name_get_node(name, branches)
                all_edges.append((from_edge, to_edge))
                gra.edge(from_edge, to_edge, label='b')
                if to_edge == None:
                    print("ERROR: BRANCH NOT MATCHED:", code, name)
                    return 0
            elif ('bz ' in code):
                print(code)
                name = code.replace("bz ", "")
                name = name.strip()
                to_edge = branch_name_get_node(name, branches)
                all_edges.append((from_edge, to_edge))
                gra.edge(from_edge, to_edge, label='bz')
                if to_edge == None:
                    print("ERROR: BRANCH NOT MATCHED:", code, name)
                    return 0
            elif ('bnz ' in code):
                print(code)
                name = code.replace("bnz ", "")
                name = name.strip()
                to_edge = branch_name_get_node(name, branches)
                all_edges.append((from_edge, to_edge))
                gra.edge(from_edge, to_edge, label='bnz')
                if to_edge == None:
                    print("ERROR: BRANCH NOT MATCHED", code, name)
                    return 0

    if debug:
        print(branches)
        print(all_edges)

    #gra.edges(all_edges) 


    #Render the final graph
    output_name = teal_file.replace(".teal", "")
    ouput_name=output_name+".pdf"
    #print(gra.source)
    gra.render(output_name, view=True)


#MAIN Program
teal_file = sys.argv[1]
generate_main_branch_graph(teal_file)
