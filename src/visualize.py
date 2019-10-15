import plotly.graph_objects as go
from network import BiNetwork, Edge, GeoNode
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import gridspec
import matplotlib
import numpy as np
from solution_generator import SolutionGenerator

def create_traces(G, edge_color = '#888', node_color = 'YlGnBu', edge_width = 0.5, add_coloring = False):
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
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale=node_color,
            reversescale=True,
            color=[],
            size=10,
            line_width=2))

    

    node_adjacencies = []
    node_text = []
    for node, adjacencies in G.adjacency():
        node_adjacencies.append(len(adjacencies))
        node_text.append('# of connections: '+str(len(adjacencies)) + "\nName: " + str(node))


    if add_coloring:
        node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    return edge_trace, node_trace

def _visualize(edge_trace, node_trace, path_edge_trace = [], path_node_trace = []):
    fig = go.Figure(data=[edge_trace, node_trace],
            layout=go.Layout(
            width = 1280,
            height = 900,
            template = 'plotly_white',
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002 ) ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
            )

    return fig
    

def visualize(G, places = None):
    '''
    Draws G and sets vertices in places to red
    '''
    edge_trace, node_trace = create_traces(G)
    fig = _visualize(edge_trace, node_trace)

    
    if places != None:
        V = []
        for place in places:
            V.append(G.get_decoded_node_with_encoded_name(G.get_encoded_node_with_name(place)))

        _, second_node_trace = create_traces(BiNetwork(V, []), node_color='reds', add_coloring=True)

        fig.add_trace(second_node_trace)
            


    fig.show()
    


def draw_convergence_figure(average_population_fitness, crossover_operators, mutation_operators, performance, execution_time):
    '''
    average_population_fitenss -> k x N array
    crossover_operators -> k array
    mutation_operators -> k array

    Draws a figure with k time series
    '''

    k = len(average_population_fitness)
    N = len(average_population_fitness[0])
    data = {'{0}, {1}'.format(x, y) : average_population_fitness[idx] for idx, (x, y) in enumerate(zip(crossover_operators, mutation_operators))}
    data['Generation'] = list(range(1, N+1))
    df = pd.DataFrame(data)

    #Setup plots
    

    plt.figure(figsize=(30, 9))
    gs = gridspec.GridSpec(1, 3, width_ratios=[4, 1, 1]) 
    
    ax0 = plt.subplot(gs[0]) #Time series
    ax1 = plt.subplot(gs[1]) #Bar chart
    ax2 = plt.subplot(gs[2]) #Exec chart

    plt.rcParams['font.family'] = 'Helvetica'
    plt.rcParams['font.sans-serif'] = 'Helvetica'
    plt.rcParams['axes.edgecolor']='#333F4B'
    plt.rcParams['axes.linewidth']=0.8
    plt.rcParams['xtick.color']='#333F4B'
    plt.rcParams['ytick.color']='#333F4B'

    ax0.spines['top'].set_color('none')
    ax0.spines['right'].set_color('none')
    ax0.spines['left'].set_smart_bounds(True)
    ax0.spines['bottom'].set_smart_bounds(True)

    ax1.spines['top'].set_color('none')
    ax1.spines['right'].set_color('none')
    ax1.spines['left'].set_smart_bounds(True)
    ax1.spines['bottom'].set_smart_bounds(True)

    ax2.spines['top'].set_color('none')
    ax2.spines['right'].set_color('none')
    ax2.spines['left'].set_smart_bounds(True)
    ax2.spines['bottom'].set_smart_bounds(True)

    
    for key in data:
        if key != 'Generation':
            ax0.plot('Generation', key, data=df)
            ax0.legend()

   
    x = np.arange(len(performance))
    width = 0.35

    ax1.tick_params(labelrotation=45)
    ax2.tick_params(labelrotation=45)
    bar_perf = ax1.bar([key for key in performance], [performance[key] for key in performance], align='center', label = 'Best Tour')
    bar_time = ax2.bar([key for key in execution_time], [execution_time[key] for key in execution_time], align='center',label='Execution Time (s)', color = 'orange')
    
    ax0.set_title('Comparison of Operators')
    ax0.set_ylabel('Average Tour Length')
    ax0.set_xlabel('Generation')

    ax1.set_title('Best Tours')
    ax2.set_title('Execution Time (s)')


    #ax1.set_xticklabels(len(performance), [key for key in performance])
    #ax1.ylabel('Length of Best Tour')
    #ax1.title('Comparison')

    plt.tight_layout()
    plt.show()




def visualize_with_path(G, path, full_path = True):

    edge_trace, node_trace = create_traces(G)

    V, ED, EF  = [], [], []

    V.append(G.get_decoded_node_with_encoded_name(path[0][0]))

    for i in range(1, len(path)):
        node_from = V[i-1]
        node_to   = G.get_decoded_node_with_encoded_name(path[i][0])
        
        V.append(node_to)

        if full_path:
            if path[i-1][1] == SolutionGenerator.DRIVE:
                shortest_path = G.shortest_path_cost_bf(node_from, node_to)
                for j in range(len(shortest_path)-1):
                    ED.append(Edge(shortest_path[j], shortest_path[j+1], 0)) #set cost to 0 since we are only visualizing
            elif path[i-1][1] == SolutionGenerator.FLY:
                EF.append(Edge(node_from, node_to, 0))
        else:
            ED.append(Edge(node_from, node_to, 0))#set cost to 0 since we are only visualizing

    drive_path_nw = BiNetwork(V, ED)
    fly_path_nw   = BiNetwork(V, EF)

    drive_path_edge_trace, _ =  create_traces(drive_path_nw, edge_color = 'red', node_color = 'Reds', edge_width=2)
    fly_path_edge_trace, _   =  create_traces(fly_path_nw, edge_color = 'green', node_color = 'Reds', edge_width=2)

    fig = _visualize(edge_trace, node_trace)

    fig.add_trace(drive_path_edge_trace)
    fig.add_trace(fly_path_edge_trace)

    fig.show()


if __name__ == "__main__":

    import sys
    sys.path.append('models')

    from geo import get_edges, get_nodes

    places = ['Rauðisandur', 'Hornstrandir', 'Varmahlíð', 'Ásbyrgi', 'Djúpivogur', 'Svartifoss', 'Landmannalaugar', 'Hvolsvöllur', 'Geysir', 'Selfoss', 'Þríhnjúkagígur', 'Reykjavík', 'Laugavegur', 'Laugardalslaug', 'Perlan', 'Kirkjufell']
    print(len(places))
    
    #Create graph
    nodes    = get_nodes('iceland')
    edge_map = get_edges('iceland')

    V, E = [], []

    node_map = {}
    for node in nodes:
        V.append(GeoNode(node[0], node[2][0], node[2][1]))
        node_map[node[0]] = V[-1]

    for place_from in edge_map:
        for place_to in edge_map[place_from]:
            E.append(Edge(node_map[place_from], node_map[place_to], edge_map[place_from][place_to]))

    nw = BiNetwork(V, E)

    
    visualize(nw)
    
