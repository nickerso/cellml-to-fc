from graphviz import Digraph

#
# Don't forget to set the path so dot can be found:
#    $> set PATH=.......\Graphviz-13.1.0-win64\bin;%PATH%
#

# dot = Digraph(comment="Hierarchical Graph", format='svg')
# dot.attr(rankdir='LR')  # TB: top-to-bottom (or use LR for left-to-right)
# dot.attr('node', shape='box', style='filled', fillcolor='lightgrey')
#
# # Nodes
# dot.node('A', 'Root')
# dot.node('B', 'Child 1')
# dot.node('C', 'Child 2')
# dot.node('D', 'Grandchild of B')
#
# # Edges
# dot.edges([('A', 'B'), ('A', 'C')])
# dot.edge('B', 'D')
#
# with dot.subgraph(name='cluster_0') as c:
#     c.attr(style='filled', color='lightblue')
#     c.node_attr.update(style='filled', color='white')
#     c.node('B', 'Child 1')
#     c.node('D', 'Grandchild')
#     c.edge('B', 'D')
#     c.attr(label='Group 1')
#
#
# # Output to SVG file
# dot.render('hierarchical_graph', cleanup=True)  # Creates hierarchical_graph.svg
# dot.view()
#
# dot = Digraph('StyledGraph', format='svg')
# dot.attr(rankdir='TB')  # Top-down layout
#
# # Default node style
# dot.attr('node', fontname='Arial', fontsize='12', style='filled', shape='box', fillcolor='lightyellow', color='black')
#
# # Custom styled nodes
# dot.node('A', 'Root Node', fillcolor='lightblue', shape='ellipse')
# dot.node('B', 'Important\n[rounded]', shape='box', style='filled,rounded', fillcolor='lightgreen', fontcolor='darkgreen')
# dot.node('C', 'Warning', fillcolor='salmon', style='filled', fontcolor='white')
# dot.node('D', '<B>HTML-style</B><BR/>Node', shape='plaintext', color='gray')
#
# # Edges
# dot.edge('A', 'B', label='leads to', color='blue')
# dot.edge('A', 'C', label='connects to', style='dashed')
# dot.edge('B', 'D')
#
# # Save as SVG
# dot.render('styled_graph', cleanup=True)
# dot.view()

dot = Digraph(format='svg')

# Add nodes with custom ID attributes
dot.node('A', 'Alpha', _attributes={'id': 'node-alpha'})
dot.node('B', 'Beta', _attributes={'id': 'node-beta'})

dot.edge('A', 'B', _attributes={'id': 'edge-alpha-beta'})

dot.render('graph_with_ids', cleanup=True)
dot.view()