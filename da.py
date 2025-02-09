import pandas as pd
import plotly.graph_objects as go
import math

def create_bar_graph(bar_data):
    df = pd.read_csv(bar_data)

    df['COUNT'] = df['COUNT'].replace({0: 'No', 1: 'Yes'})

    df_grouped = df.groupby(['LABEL', 'COUNT']).size().unstack(fill_value=0)

    df_grouped = df_grouped[['No', 'Yes']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_grouped.index,
        x=df_grouped['No'],
        name='No',
        orientation='h',
        marker_color='red'
    ))

    fig.add_trace(go.Bar(
        y=df_grouped.index,
        x=df_grouped['Yes'],
        name='Yes',
        orientation='h',
        marker_color='blue'
    ))

    fig.update_layout(
        barmode='stack',
        title='Count of Yes/No per Label',
        xaxis_title='Count',
        yaxis_title='Label',
        legend_title='LEGEND HERE',

        annotations=[
            dict(
                x=df_grouped['No'][i] / 2,
                y=label,
                text=str(df_grouped['No'][i]),
                showarrow=False,
                font=dict(color='white')
            ) for i, label in enumerate(df_grouped.index) if df_grouped['No'][i] > 0
        ] + [
            dict(
                x=df_grouped['No'][i] + df_grouped['Yes'][i] / 2,
                y=label,
                text=str(df_grouped['Yes'][i]),
                showarrow=False,
                font=dict(color='white')
            ) for i, label in enumerate(df_grouped.index) if df_grouped['Yes'][i] > 0
        ]
    )

    fig.show()


def create_sankey_diagram(sankey_data):

    df = pd.read_csv(sankey_data)

    source_cols = ['PS', 'OMP', 'CNP', 'NRP', 'NMCCC', 'PEC', 'NCDM', 'RGS']

    target_cols = ['Reg', 'Aca', 'Oth']

    label_col = 'LABEL'

    all_nodes = source_cols + df[label_col].tolist() + target_cols

    node_to_index = {node: i for i, node in enumerate(all_nodes)}

    sources = []
    targets = []
    values = []
    link_colors = []

    for source_col in source_cols:
        for i, row in df.iterrows():
            label = row[label_col]
            source_index = node_to_index[source_col]
            intermediate_index = node_to_index[label]
            intermediate_value = row[source_col]
            
            if intermediate_value> 0:
                sources.append(source_index)
                targets.append(intermediate_index)
                values.append(intermediate_value)
                link_colors.append('rgba(150, 150, 150, 0.3)')

            
            for target_col in target_cols:
                target_index = node_to_index[target_col]
                target_value = row[target_col]

                if target_value > 0:
                    sources.append(intermediate_index)
                    targets.append(target_index)
                    values.append(target_value)
                    link_colors.append('rgba(150, 150, 150, 0.3)')

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
        ))])

    fig.update_layout(title_text="Sankey Diagram of Assignment Data", font_size=10)
    fig.show()
    

def create_network_graph(network_data):

    df = pd.read_csv(network_data)

    all_nodes = df.columns[1:].tolist()
    pentagram_nodes = ['D', 'F', 'I', 'N', 'S']
    green_nodes = ['BIH', 'GEO', 'ISR', 'MNE', 'SRB', 'CHE', 'TUR', 'UKR', 'GBR', 'AUS', 'HKG', 'ASU']
    yellow_nodes = ['AUT', 'BEL', 'BGR', 'HRV', 'CZE', 'EST', 'FRA', 'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LUX', 'NLD', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP']

    center_x = 0
    center_y = 0
    radius = 1
    pentagram_positions = {}
    for i, node in enumerate(pentagram_nodes):
        angle = 2 * math.pi * i / len(pentagram_nodes)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        pentagram_positions[node] = (x, y)

    outer_radius = 3
    all_other_nodes = green_nodes + yellow_nodes
    other_node_positions = {}
    for i, node in enumerate(all_other_nodes):
        angle = 2 * math.pi * i / len(all_other_nodes)
        x = center_x + outer_radius * math.cos(angle)
        y = center_y + outer_radius * math.sin(angle)
        other_node_positions[node] = (x, y)


    node_positions = {**pentagram_positions, **other_node_positions}

    edges = []
    for i, row in df.iterrows():
        source = row['LABELS']
        for target in df.columns[1:]:
            if row[target] > 0:
                edges.append((source, target))

    edge_x = []
    edge_y = []
    for edge in edges:
        x0, y0 = node_positions[edge[0]]
        x1, y1 = node_positions[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_color = []
    node_text = []
    for node in all_nodes:
        x, y = node_positions[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        if node in pentagram_nodes:
            node_color.append('blue')
        elif node in green_nodes:
            node_color.append('green')
        elif node in yellow_nodes:
            node_color.append('gold')
        else:
            node_color.append('gray')
        
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="bottom center",
        marker=dict(
            showscale=False,
            colorscale='Viridis',
            reversescale=True,
            color=node_color,
            size=30,
            line_width=1,
            line_color = 'black')
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )
    
    fig.show()

create_bar_graph('bar_assignment.csv')
create_sankey_diagram('sankey_assignment.csv')
create_network_graph('networks_assignment.to_csv')