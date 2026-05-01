import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def generate_network_graph(file_path, output_image, sheet_name=None):
    """
    Reads an Excel file and generates a network graph with edge labels.
    """
    try:
        print(f"Reading data from {file_path}...")
        
        # Try to find a sheet with 'Input' and 'Output'
        xl = pd.ExcelFile(file_path)
        
        if sheet_name is not None:
            sheet_name_to_use = sheet_name
        else:
            sheet_name_to_use = 'Edges'
            if 'Edges' not in xl.sheet_names:
                # Let's search for the first sheet that has Input and Output
                for sheet in xl.sheet_names:
                    df_temp = pd.read_excel(file_path, sheet_name=sheet)
                    if 'Input' in df_temp.columns and 'Output' in df_temp.columns:
                        sheet_name_to_use = sheet
                        break
                    df_temp = pd.read_excel(file_path, sheet_name=sheet, header=1)
                    if 'Input' in df_temp.columns and 'Output' in df_temp.columns:
                        sheet_name_to_use = sheet
                        break
                else:
                    sheet_name_to_use = xl.sheet_names[-1] # Fallback to the last sheet
                
        df_edges = pd.read_excel(file_path, sheet_name=sheet_name_to_use)
        if 'Input' not in df_edges.columns or 'Output' not in df_edges.columns:
            df_edges = pd.read_excel(file_path, sheet_name=sheet_name_to_use, header=1)
        
        # Read Vertices (if exists)
        has_attributes = False
        df_vertices = None
        if 'Vertices' in xl.sheet_names:
            df_vertices = pd.read_excel(file_path, sheet_name='Vertices')
            has_attributes = True
            print("Vertices sheet found. Using attributes for coloring.")
        else:
            print("Vertices sheet not found. Using default coloring.")

        # Verify columns in Edges
        required_cols = ['Input', 'Output']
        if not all(col in df_edges.columns for col in required_cols):
            print(f"Error: Sheet '{sheet_name_to_use}' must contain columns {required_cols}. Found: {df_edges.columns.tolist()}")
            return

        # Initialize Directed Graph
        G = nx.DiGraph()
        
        print("Building graph...")
        # Add edges
        edge_labels = {}
        for _, row in df_edges.iterrows():
            source = row['Input']
            target = row['Output']
            
            if pd.notna(source) and pd.notna(target):
                label = row['Label'] if 'Label' in df_edges.columns and pd.notna(row['Label']) else ""
                G.add_edge(source, target, label=label)
                if label:
                    edge_labels[(source, target)] = str(label)
        
        if G.number_of_nodes() == 0:
            print("Graph is empty. Check data.")
            return

        # Attribute Coloring Logic
        node_colors = []
        if has_attributes and df_vertices is not None:
            if 'Node' in df_vertices.columns and 'Attribute' in df_vertices.columns:
                attr_map = dict(zip(df_vertices['Node'], df_vertices['Attribute']))
                unique_attrs = df_vertices['Attribute'].dropna().unique()
                palette = ['skyblue', 'lightgreen', 'salmon', 'wheat', 'violet', 'gold', 'cyan', 'pink']
                color_map = {attr: palette[i % len(palette)] for i, attr in enumerate(unique_attrs)}
                
                for node in G.nodes():
                    attr = attr_map.get(node, 'Unknown')
                    node_colors.append(color_map.get(attr, 'lightgray'))
            else:
                node_colors = ['skyblue'] * len(G.nodes())
        else:
            node_colors = ['skyblue'] * len(G.nodes())

        print(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

        # Visualization
        plt.figure(figsize=(20, 18))
        
        # Identify the most connected node (central node)
        degrees = dict(G.degree())
        central_node = max(degrees, key=degrees.get)
        
        # Order outer nodes so those with shared edges/neighbors are adjacent
        other_nodes = [n for n in G.nodes() if n != central_node]
        U = G.to_undirected()
        
        ordered_nodes = []
        if other_nodes:
            unvisited = set(other_nodes)
            current = other_nodes[0]
            ordered_nodes.append(current)
            unvisited.remove(current)
            
            while unvisited:
                best_node = None
                best_sim = -1
                for v in unvisited:
                    sim = len(list(nx.common_neighbors(U, current, v)))
                    if U.has_edge(current, v):
                        sim += 2
                    if sim > best_sim:
                        best_sim = sim
                        best_node = v
                current = best_node
                ordered_nodes.append(current)
                unvisited.remove(current)
                
        # Use a shell layout with the central node in the middle, and others in a circle
        pos = nx.shell_layout(G, nlist=[[central_node], ordered_nodes])
        
        # Balance node size so they are prominent but leave room for labels
        nx.draw_networkx_nodes(G, pos, node_size=3500, node_color=node_colors, edgecolors='gray')
        
        # Pass node_size to edges so arrows don't hide under the nodes
        nx.draw_networkx_edges(G, pos, node_size=3500, width=2, edge_color='gray', arrows=True, arrowstyle='-|>', arrowsize=25, connectionstyle='arc3, rad=0.1')
        
        # Node labels
        nx.draw_networkx_labels(G, pos, font_size=11, font_weight="bold", font_family='sans-serif')
        
        if edge_labels:
            # Shift labels toward the outer nodes (label_pos=0.75) where there is more space
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_color='darkred', label_pos=0.75, bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='lightgray', alpha=0.9))

        plt.title("Network Graph Visualization with Edge Labels")
        plt.axis('off')
        plt.tight_layout()
        
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Graph visualization saved to {output_image}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_network_graph('Datos ICMI 27.xlsx', 'Graph_ICMI_Datos.png', sheet_name='Datos')
