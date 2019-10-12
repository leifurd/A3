import plotly.graph_objects as go
from network import BiNetwork, Edge


def create_traces(G, edge_color = '#888', node_color = 'YlGnBu', edge_width = 0.5):
    edge_x = []
    edge_y = []
    for edge in G.E:
        x0, y0 = edge.node_from.x, edge.node_from.y #G.node[edge[0]]['pos']
        x1, y1 = edge.node_to.x, edge.node_to.y #G.node[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=edge_width, color=edge_color),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.V:
        x, y = node.x, node.y #G.node[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale=node_color,
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    
    node_adjacencies = []
    node_text = []
    for node, adjacencies in G.adjacency():
        node_adjacencies.append(len(adjacencies))
        node_text.append('# of connections: '+str(len(adjacencies)) + "\nName: " + str(node))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    return edge_trace, node_trace

def _visualize(edge_trace, node_trace, path_edge_trace = [], path_node_trace = []):
    fig = go.Figure(data=[edge_trace, node_trace],
            layout=go.Layout(
            title='Network of Tourist Attractions in Iceland',
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Iceland",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002 ) ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
            )
    return fig
    

def visualize(G):
    edge_trace, node_trace = create_traces(G)
    _visualize(edge_trace, node_trace).show()
    


    

def visualize_with_path(G, path, full_path = True):

    edge_trace, node_trace = create_traces(G)

    V, E = [], []

    V.append(G.get_decoded_node_with_encoded_name(path[0][0]))

    for i in range(1, len(path)):
        node_from = V[i-1]
        node_to   = G.get_decoded_node_with_encoded_name(path[i][0])
        
        V.append(node_to)
        if full_path:
            shortest_path = G.shortest_path_cost_bf(node_from, node_to)
            for j in range(len(shortest_path)-1):
                E.append(Edge(shortest_path[j], shortest_path[j+1], 0)) #set cost to 0 since we are only visualizing
        else:
            E.append(Edge(node_from, node_to, 0))#set cost to 0 since we are only visualizing

    path_nw = BiNetwork(V, E)
    path_edge_trace, path_node_trace =  create_traces(path_nw, edge_color = 'red', node_color = 'Reds', edge_width=0.5)

    fig = _visualize(edge_trace, node_trace)

    fig.add_trace(path_edge_trace)

    fig.show()



    