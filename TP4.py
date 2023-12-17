import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import os
from itertools import permutations
import time

# Get the absolute path to the image file
current_directory = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_directory, "background_image.png")

# Initialize G as a global variable
G = nx.Graph()


def load_image(file_path):
    try:
        image = Image.open(file_path)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading image: {str(e)}")


def draw_graph(nodes, edges, costs, ax):
    global G  # Declare G as a global variable
    G = nx.Graph()

    # Add nodes to the graph
    G.add_nodes_from(nodes)

    # Add edges with corresponding costs
    for edge, cost in zip(edges, costs):
        G.add_edge(edge[0], edge[1], weight=cost)

    # Define the layout for better visualization
    pos = nx.spring_layout(G, k=2)  # Increase the spacing between nodes

    # Draw the graph with adjusted parameters
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=1000,  # Increase node size
        node_color='skyblue',
        font_size=14,  # Increase font size
        font_color='black',
        font_weight='bold',  # Make the font bold
        ax=ax,
    )

    # Add edge labels with costs
    edge_labels = {(edge[0], edge[1]): cost for edge, cost in zip(edges, costs)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=12, font_color='red')


def on_submit():
    try:
        # Get user input for nodes, edges, and costs
        nodes_input = entry_nodes.get().split()
        edges_input = entry_edges.get().split()
        costs_input = entry_costs.get().split()

        # Convert costs to integers
        costs = list(map(int, costs_input))

        # Create edges as pairs
        edges = [(edges_input[i], edges_input[i + 1]) for i in range(0, len(edges_input), 2)]

        # Extract unique nodes from edges
        nodes = set(node for edge in edges for node in edge)

        # Check if any input node is not in the graph
        invalid_nodes = set(nodes_input) - nodes
        if invalid_nodes:
            messagebox.showerror("Error", f"Invalid input: Nodes {', '.join(invalid_nodes)} are not defined in the graph.")
            return

        # Clear the previous graph
        ax.clear()

        # Draw the new graph
        draw_graph(list(nodes), edges, costs, ax)

        # Update the canvas
        canvas.draw()

    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {str(e)}")

def greedy_tsp(graph, start_node):
    current_node = start_node
    visited_nodes = [current_node]
    total_cost = 0

    while len(visited_nodes) < len(graph.nodes()):
        costs = [(neighbor, graph[current_node][neighbor]['weight']) for neighbor in graph.neighbors(current_node) if
                 neighbor not in visited_nodes]
        if not costs:
            break

        next_node, cost = min(costs, key=lambda x: x[1])

        total_cost += cost
        current_node = next_node
        visited_nodes.append(current_node)

    total_cost += graph[current_node][visited_nodes[0]]['weight']

    return visited_nodes + [visited_nodes[0]], total_cost


def tsp_heuristic(start_node, result_label):
    try:
        global G  # Access the global variable G

        start_time = time.time()  # Record start time

        # Apply the heuristic TSP algorithm (nearest neighbor) with the specified start node
        tour, cost = greedy_tsp(G, start_node)

        end_time = time.time()  # Record end time
        execution_time = end_time - start_time

        if tour:
            result_label.config(
                text=f"Heuristic TSP Solution (starting from {start_node}): {tour}\nTotal Cost: {cost}\nExecution Time: {execution_time:.6f} seconds",
                font=("Helvetica", 14),  # Increase font size
            )
        else:
            result_label.config(text="Unable to find a solution.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")



def tsp_exact(graph, result_label):
    try:
        nodes = list(map(str, graph.nodes()))  # Convert nodes to strings
        min_cost = float('inf')
        best_tour = None

        start_time = time.time()  # Record start time

        for tour in permutations(nodes):
            cost = calculate_tour_cost(graph, tour)
            if cost < min_cost:
                min_cost = cost
                best_tour = tour

        end_time = time.time()  # Record end time
        execution_time = end_time - start_time

        result_label.config(
            text=f"Exact TSP Solution: {best_tour}\nTotal Cost: {min_cost}\nExecution Time: {execution_time:.6f} seconds",
            font=("Helvetica", 14),  # Increase font size
        )

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")



def calculate_tour_cost(graph, tour):
    cost = 0
    for i in range(len(tour) - 1):
        cost += graph[tour[i]][tour[i + 1]]['weight']
    cost += graph[tour[-1]][tour[0]]['weight']
    return cost


# Create the main window
root = tk.Tk()
root.title("TSP Problem")
root.geometry("600x750")  # Set the window size (width x height)

# Set a background image using Pillow
background_image = load_image(image_path)
background_label = tk.Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)

# Create labels and entry widgets for nodes, edges, and costs
label_nodes = ttk.Label(root, text="Nodes:", font=("Helvetica", 14), style='Label.TLabel')  # Increase font size
label_edges = ttk.Label(root, text="Edges (pairs, e.g., 'A B C D'):", font=("Helvetica", 14), style='Label.TLabel')  # Increase font size
label_costs = ttk.Label(root, text="Costs (space-separated):", font=("Helvetica", 14), style='Label.TLabel')  # Increase font size

entry_nodes = ttk.Entry(root, width=30, font=("Helvetica", 14))  # Increase font size
entry_edges = ttk.Entry(root, width=30, font=("Helvetica", 14))  # Increase font size
entry_costs = ttk.Entry(root, width=30, font=("Helvetica", 14))  # Increase font size

# Create a submit button with custom style
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 14), foreground='blue', background='blue', padding=(10, 5))
submit_button = ttk.Button(root, text="Draw Graph", command=on_submit, style='TButton')

# Create a frame for the graph
frame_graph = ttk.Frame(root)

# Create a matplotlib figure and canvas for embedding the graph
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=frame_graph)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Place widgets using the grid layout
label_nodes.grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_nodes.grid(row=0, column=1, padx=10, pady=5, sticky="w")
label_edges.grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_edges.grid(row=1, column=1, padx=10, pady=5, sticky="w")
label_costs.grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_costs.grid(row=2, column=1, padx=10, pady=5, sticky="w")
submit_button.grid(row=3, column=0, columnspan=2, pady=10)
frame_graph.grid(row=4, column=0, columnspan=2, pady=10)

result_label = ttk.Label(root, text="", font=("Helvetica", 14), style='Result.TLabel')  # Increase font size
label_tsp_start = ttk.Label(root, text="TSP Start Node:", font=("Helvetica", 14), style='Label.TLabel')  # Increase font size
entry_tsp_start = ttk.Entry(root, width=30, font=("Helvetica", 14))  # Increase font size
tsp_button = ttk.Button(
    root,
    text="Apply TSP Heuristic",
    command=lambda: tsp_heuristic(entry_tsp_start.get(), result_label),
    style='TButton',
)
exact_button = ttk.Button(
    root, text="Apply Exact TSP", command=lambda: tsp_exact(G, result_label), style='TButton'
)

label_tsp_start.grid(row=8, column=0, padx=10, pady=5, sticky="w")
entry_tsp_start.grid(row=8, column=1, padx=10, pady=5, sticky="w")
tsp_button.grid(row=9, column=0, columnspan=2, pady=10)
exact_button.grid(row=10, column=0, columnspan=2, pady=10)
result_label.grid(row=11, column=0, columnspan=2, pady=5)

# Configure custom styles for labels
style.configure('Label.TLabel', foreground='white', background='blue')  # Label style
style.configure('Result.TLabel', foreground='white', background='blue')  # Result label style

# Run the main loop
root.mainloop()
