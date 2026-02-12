"""
NETWORK VISUALIZATIONS FOR TERRITORIAL CONTROL
Creates multiple network types from UCDP violence data:
1. Competitive Territorial Network (who controls where)
2. Alliance Shift Network (who fights whom)
3. Spatial Co-occurrence Network (actors in same locations)
4. Temporal Evolution Network (control changes over time)
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
from collections import defaultdict
import yaml

# ============================================================================
# 1. LOAD DATA 
# ============================================================================

def load_ucdp_ged_data(filepath='ucdp_ged_car.csv'):
    """Load UCDP GED data"""
    df = pd.read_csv(filepath)
    
    # Filter for CAR
    if 'country' in df.columns:
        df = df[df['country'].str.contains('Central African Republic|CAR', case=False, na=False)].copy()
    
    # Date handling
    if 'year' in df.columns:
        df['date'] = pd.to_datetime(df['year'].astype(str) + '-01-01')
    
    # Total deaths
    death_cols = ['deaths_a', 'deaths_b', 'deaths_civilians', 'deaths_unknown']
    death_cols_available = [col for col in death_cols if col in df.columns]
    
    if death_cols_available:
        df['total_deaths'] = df[death_cols_available].sum(axis=1)
    elif 'best' in df.columns:
        df['total_deaths'] = df['best']
    
    # Actor column
    if 'side_a' in df.columns:
        df['actor'] = df['side_a']
    
    # Location
    if 'adm_1' in df.columns:
        df['location_name'] = df['adm_1']
    
    return df

def infer_territorial_control(violence_data, location, time_window):
    """Infer control from violence"""
    mask = (
        (violence_data['location_name'] == location) &
        (violence_data['date'] >= time_window[0]) &
        (violence_data['date'] <= time_window[1])
    )
    
    subset = violence_data[mask].copy()
    
    if len(subset) == 0:
        return {'control_shares': {}, 'total_deaths': 0}
    
    actor_deaths = subset.groupby('actor')['total_deaths'].sum()
    total_deaths = actor_deaths.sum()
    
    if total_deaths > 0:
        control_shares = (actor_deaths / total_deaths * 100).to_dict()
    else:
        actor_counts = subset.groupby('actor').size()
        control_shares = (actor_counts / len(subset) * 100).to_dict()
    
    return {
        'control_shares': control_shares,
        'total_deaths': float(total_deaths)
    }

# ============================================================================
# 2. NETWORK 1: COMPETITIVE TERRITORIAL NETWORK
# ============================================================================

def build_competitive_territorial_network(violence_data, time_window=None):
    """
    Build network showing territorial competition
    
    Nodes: Actor-Location pairs
    Edges: Shared presence in same location (competition)
    Edge weight: Intensity of competition (both commit violence there)
    """
    
    if time_window:
        data = violence_data[
            (violence_data['date'] >= time_window[0]) &
            (violence_data['date'] <= time_window[1])
        ].copy()
    else:
        data = violence_data.copy()
    
    G = nx.Graph()
    
    # Get unique locations
    locations = data['location_name'].unique()
    
    for location in locations:
        # Get actors active in this location
        loc_data = data[data['location_name'] == location]
        actors = loc_data['actor'].unique()
        
        if len(actors) < 2:
            continue  # Skip if only one actor (no competition)
        
        # Add nodes for each actor-location
        for actor in actors:
            node_id = f"{actor}@{location}"
            
            actor_violence = loc_data[loc_data['actor'] == actor]
            deaths = actor_violence['total_deaths'].sum()
            events = len(actor_violence)
            
            G.add_node(node_id,
                      actor=actor,
                      location=location,
                      deaths=deaths,
                      events=events)
        
        # Add edges between competing actors in same location
        for i, actor1 in enumerate(actors):
            for actor2 in actors[i+1:]:
                node1 = f"{actor1}@{location}"
                node2 = f"{actor2}@{location}"
                
                # Edge weight = sum of violence by both actors
                violence1 = loc_data[loc_data['actor'] == actor1]['total_deaths'].sum()
                violence2 = loc_data[loc_data['actor'] == actor2]['total_deaths'].sum()
                competition_intensity = violence1 + violence2
                
                G.add_edge(node1, node2,
                          weight=competition_intensity,
                          location=location)
    
    return G

def visualize_competitive_territorial_network(G, save_path='network_territorial_competition.png'):
    """Visualize competitive territorial network"""
    
    if len(G.nodes()) == 0:
        print("No competitive relationships to visualize")
        return
    
    fig, ax = plt.subplots(figsize=(20, 16))
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Get unique actors for coloring
    actors = list(set([G.nodes[node]['actor'] for node in G.nodes()]))
    colors = plt.cm.Set3(np.linspace(0, 1, len(actors)))
    actor_colors = dict(zip(actors, colors))
    
    # Draw edges (competition)
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    
    for u, v, data in G.edges(data=True):
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        width = 0.5 + (data['weight'] / max_weight) * 5
        
        ax.plot(x, y, 'gray', linewidth=width, alpha=0.4, zorder=1)
    
    # Draw nodes
    for node in G.nodes():
        actor = G.nodes[node]['actor']
        location = G.nodes[node]['location']
        deaths = G.nodes[node]['deaths']
        
        color = actor_colors[actor]
        size = 100 + deaths * 2
        
        ax.scatter(pos[node][0], pos[node][1],
                  s=size,
                  c=[color],
                  alpha=0.8,
                  edgecolors='black',
                  linewidth=2,
                  zorder=2)
        
        # Label high-violence nodes
        if deaths > 50:
            ax.text(pos[node][0], pos[node][1] + 0.05,
                   f"{actor[:10]}\n{location[:15]}",
                   fontsize=7,
                   ha='center',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    # Legend
    legend_elements = [mpatches.Patch(color=actor_colors[actor], label=actor)
                      for actor in actors]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
    
    ax.set_title('Competitive Territorial Network\n(Nodes=Actor@Location, Edges=Competition)',
                fontsize=16, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {save_path}")
    plt.close()

# ============================================================================
# 3. NETWORK 2: CONFLICT DYAD NETWORK (Who Fights Whom)
# ============================================================================

def build_conflict_dyad_network(violence_data, time_window=None):
    """
    Build network showing which actors fight each other
    
    Nodes: Actors
    Edges: Direct conflict (both sides in violence events)
    Edge weight: Number of conflicts
    """
    
    if time_window:
        data = violence_data[
            (violence_data['date'] >= time_window[0]) &
            (violence_data['date'] <= time_window[1])
        ].copy()
    else:
        data = violence_data.copy()
    
    G = nx.Graph()
    
    # If we have side_b data, use it for dyadic conflicts
    if 'side_b' in data.columns:
        # Direct conflicts between side_a and side_b
        for idx, row in data.iterrows():
            actor1 = row['actor']
            actor2 = row.get('side_b')
            
            if pd.notna(actor2) and actor1 != actor2:
                deaths = row['total_deaths']
                
                # Add nodes
                if not G.has_node(actor1):
                    G.add_node(actor1, total_deaths=0, num_conflicts=0)
                if not G.has_node(actor2):
                    G.add_node(actor2, total_deaths=0, num_conflicts=0)
                
                # Add/update edge
                if G.has_edge(actor1, actor2):
                    G[actor1][actor2]['weight'] += 1
                    G[actor1][actor2]['total_deaths'] += deaths
                else:
                    G.add_edge(actor1, actor2,
                             weight=1,
                             total_deaths=deaths)
                
                # Update node attributes
                G.nodes[actor1]['total_deaths'] += deaths
                G.nodes[actor1]['num_conflicts'] += 1
                G.nodes[actor2]['total_deaths'] += deaths
                G.nodes[actor2]['num_conflicts'] += 1
    else:
        # Infer conflicts from co-occurrence in same locations
        # (Actors in same location at same time likely fighting)
        location_time_actors = defaultdict(set)
        
        for idx, row in data.iterrows():
            key = (row['location_name'], row['date'])
            location_time_actors[key].add(row['actor'])
        
        for (location, date), actors in location_time_actors.items():
            actors_list = list(actors)
            
            for i, actor1 in enumerate(actors_list):
                if not G.has_node(actor1):
                    G.add_node(actor1, total_violence=0)
                
                for actor2 in actors_list[i+1:]:
                    if not G.has_node(actor2):
                        G.add_node(actor2, total_violence=0)
                    
                    # Inferred conflict
                    if G.has_edge(actor1, actor2):
                        G[actor1][actor2]['weight'] += 1
                    else:
                        G.add_edge(actor1, actor2, weight=1)
    
    return G

def visualize_conflict_dyad_network(G, save_path='network_conflict_dyads.png'):
    """Visualize who fights whom"""
    
    if len(G.nodes()) == 0:
        print("No conflict relationships to visualize")
        return
    
    fig, ax = plt.subplots(figsize=(16, 14))
    
    # Layout - circular for dyadic relationships
    pos = nx.circular_layout(G)
    
    # Draw edges (conflicts)
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    
    for u, v, data in G.edges(data=True):
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        width = 0.5 + (data['weight'] / max_weight) * 8
        
        ax.plot(x, y, 'red', linewidth=width, alpha=0.5, zorder=1)
    
    # Node sizes by total involvement
    node_sizes = []
    for node in G.nodes():
        if 'num_conflicts' in G.nodes[node]:
            size = 200 + G.nodes[node]['num_conflicts'] * 50
        else:
            size = 200 + G.degree(node) * 50
        node_sizes.append(size)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos,
                          node_size=node_sizes,
                          node_color='lightblue',
                          edgecolors='black',
                          linewidths=2,
                          alpha=0.9,
                          ax=ax)
    
    # Labels
    nx.draw_networkx_labels(G, pos,
                           font_size=10,
                           font_weight='bold',
                           ax=ax)
    
    ax.set_title('Conflict Dyad Network\n(Who Fights Whom)',
                fontsize=16, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {save_path}")
    plt.close()

# ============================================================================
# 4. NETWORK 3: SPATIAL CO-OCCURRENCE NETWORK
# ============================================================================

def build_spatial_cooccurrence_network(violence_data, time_window=None):
    """
    Build network showing which actors operate in overlapping territories
    
    Nodes: Actors
    Edges: Shared operational areas
    Edge weight: Number of shared locations
    """
    
    if time_window:
        data = violence_data[
            (violence_data['date'] >= time_window[0]) &
            (violence_data['date'] <= time_window[1])
        ].copy()
    else:
        data = violence_data.copy()
    
    G = nx.Graph()
    
    # Get actor presence by location
    actor_locations = defaultdict(set)
    actor_violence = defaultdict(int)
    
    for idx, row in data.iterrows():
        actor = row['actor']
        location = row['location_name']
        
        actor_locations[actor].add(location)
        actor_violence[actor] += row['total_deaths']
    
    # Add nodes
    for actor, locations in actor_locations.items():
        G.add_node(actor,
                  num_locations=len(locations),
                  total_violence=actor_violence[actor],
                  locations=list(locations))
    
    # Add edges for shared locations
    actors = list(actor_locations.keys())
    for i, actor1 in enumerate(actors):
        for actor2 in actors[i+1:]:
            # Count shared locations
            shared = actor_locations[actor1] & actor_locations[actor2]
            
            if len(shared) > 0:
                # Jaccard similarity
                union = actor_locations[actor1] | actor_locations[actor2]
                jaccard = len(shared) / len(union)
                
                G.add_edge(actor1, actor2,
                          shared_locations=len(shared),
                          jaccard_similarity=jaccard,
                          weight=len(shared))
    
    return G

def visualize_spatial_cooccurrence_network(G, save_path='network_spatial_cooccurrence.png'):
    """Visualize spatial co-occurrence"""
    
    if len(G.nodes()) == 0:
        print("No spatial relationships to visualize")
        return
    
    fig, ax = plt.subplots(figsize=(16, 14))
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Draw edges (shared territories)
    for u, v, data in G.edges(data=True):
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        
        shared = data['shared_locations']
        jaccard = data['jaccard_similarity']
        
        # Edge width = number of shared locations
        width = 0.5 + shared * 0.5
        
        # Edge color intensity = Jaccard similarity
        alpha = 0.3 + jaccard * 0.6
        
        ax.plot(x, y, 'green', linewidth=width, alpha=alpha, zorder=1)
    
    # Node sizes by territorial reach
    node_sizes = [200 + G.nodes[node]['num_locations'] * 50 for node in G.nodes()]
    
    # Node colors by violence intensity
    node_violence = [G.nodes[node]['total_violence'] for node in G.nodes()]
    
    nodes = nx.draw_networkx_nodes(G, pos,
                                   node_size=node_sizes,
                                   node_color=node_violence,
                                   cmap='YlOrRd',
                                   edgecolors='black',
                                   linewidths=2,
                                   alpha=0.9,
                                   ax=ax)
    
    # Colorbar
    cbar = plt.colorbar(nodes, ax=ax)
    cbar.set_label('Total Violence (Deaths)', rotation=270, labelpad=20)
    
    # Labels
    nx.draw_networkx_labels(G, pos,
                           font_size=9,
                           font_weight='bold',
                           ax=ax)
    
    ax.set_title('Spatial Co-occurrence Network\n(Node size=Territorial reach, Edge=Shared locations)',
                fontsize=16, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

# ============================================================================
# 5. NETWORK 4: TEMPORAL CONTROL CHANGE NETWORK
# ============================================================================

def build_temporal_control_network(violence_data, time_periods):
    """
    Build network showing how control changes over time
    
    Nodes: Actor-Location-Time
    Edges: Control transitions (same location, different times)
    """
    
    G = nx.DiGraph()  # Directed for temporal flow
    
    locations = violence_data['location_name'].unique()
    
    for location in locations:
        loc_data = violence_data[violence_data['location_name'] == location]
        
        # For each time period, infer control
        for i, (start, end) in enumerate(time_periods):
            control = infer_territorial_control(loc_data, location, (start, end))
            
            if not control['control_shares']:
                continue
            
            # Add nodes for this period
            for actor, share in control['control_shares'].items():
                node_id = f"{actor}@{location}@T{i}"
                
                G.add_node(node_id,
                          actor=actor,
                          location=location,
                          time_period=i,
                          control_share=share,
                          date=start)
            
            # Connect to previous period 
            if i > 0:
                prev_control = infer_territorial_control(loc_data, location, 
                                                        (time_periods[i-1][0], time_periods[i-1][1]))
                
                # Current actors
                current_actors = set(control['control_shares'].keys())
                previous_actors = set(prev_control['control_shares'].keys())
                
                # Control transitions
                for actor in current_actors:
                    current_node = f"{actor}@{location}@T{i}"
                    
                    if actor in previous_actors:
                        # Actor maintained presence
                        prev_node = f"{actor}@{location}@T{i-1}"
                        
                        change = control['control_shares'][actor] - prev_control['control_shares'][actor]
                        
                        G.add_edge(prev_node, current_node,
                                  change=change,
                                  transition_type='maintained')
                    else:
                        # Actor entered location
                        # Connect to all previous actors 
                        for prev_actor in previous_actors:
                            prev_node = f"{prev_actor}@{location}@T{i-1}"
                            G.add_edge(prev_node, current_node,
                                     change=control['control_shares'][actor],
                                     transition_type='entered')
    
    return G

def visualize_temporal_control_network(G, save_path='network_temporal_control.png'):
    """Visualize control changes over time"""
    
    if len(G.nodes()) == 0:
        print("No temporal control data to visualize")
        return
    
    fig, ax = plt.subplots(figsize=(20, 12))
    
    # Layout - hierarchical by time period
    # Group nodes by time period for layered layout
    time_periods = set([G.nodes[node]['time_period'] for node in G.nodes()])
    num_periods = len(time_periods)
    
    pos = {}
    for node in G.nodes():
        t = G.nodes[node]['time_period']
        
        # X position = time period
        x = t * 2
        
        # Y position = actor (to separate actors vertically)
        actor = G.nodes[node]['actor']
        
        # Get all actors
        all_actors = sorted(set([G.nodes[n]['actor'] for n in G.nodes()]))
        y = all_actors.index(actor) * 0.5
        
        pos[node] = (x, y)
    
    # Draw edges (control transitions)
    for u, v, data in G.edges(data=True):
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        
        transition_type = data.get('transition_type', 'maintained')
        
        if transition_type == 'maintained':
            color = 'green'
            alpha = 0.6
        else:
            color = 'red'
            alpha = 0.4
        
        ax.annotate('',
                   xy=(pos[v][0], pos[v][1]),
                   xytext=(pos[u][0], pos[u][1]),
                   arrowprops=dict(arrowstyle='->', color=color, 
                                 linewidth=2, alpha=alpha))
    
    # Draw nodes
    for node in G.nodes():
        x, y = pos[node]
        share = G.nodes[node]['control_share']
        
        size = 100 + share * 10
        
        ax.scatter(x, y, s=size, c='lightblue',
                  edgecolors='black', linewidths=2,
                  alpha=0.8, zorder=2)
        
        # Label
        actor = G.nodes[node]['actor']
        ax.text(x, y, actor[:10], fontsize=7, ha='center', va='center')
    
    ax.set_title('Temporal Control Network\n(Green=Maintained, Red=Takeover)',
                fontsize=16, fontweight='bold')
    ax.set_xlabel('Time Period', fontsize=12)
    ax.set_ylabel('Actors', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {save_path}")
    plt.close()

# ============================================================================
# 6. MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*70)
    print("NETWORK VISUALIZATIONS FROM TERRITORIAL CONTROL DATA")
    print("="*70)
    
    # Load data
    print("Loading UCDP data...")
    try:
        violence_data = load_ucdp_ged_data('ucdp_ged_car.csv')
        print(f"  ✓ Loaded {len(violence_data)} violence events")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Build and visualize networks
    print("Building networks...")
    
    # Network 1: Competitive Territorial
    print("\n  1. Competitive Territorial Network...")
    G_territorial = build_competitive_territorial_network(violence_data)
    print(f"     ✓ {len(G_territorial.nodes())} nodes, {len(G_territorial.edges())} edges")
    visualize_competitive_territorial_network(G_territorial)
    
    # Network 2: Conflict Dyads
    print("\n  2. Conflict Dyad Network...")
    G_dyad = build_conflict_dyad_network(violence_data)
    print(f"     ✓ {len(G_dyad.nodes())} nodes, {len(G_dyad.edges())} edges")
    visualize_conflict_dyad_network(G_dyad)
    
    # Network 3: Spatial Co-occurrence
    print("\n  3. Spatial Co-occurrence Network...")
    G_spatial = build_spatial_cooccurrence_network(violence_data)
    print(f"     ✓ {len(G_spatial.nodes())} nodes, {len(G_spatial.edges())} edges")
    visualize_spatial_cooccurrence_network(G_spatial)
    
    # Network 4: Temporal Control Changes
    print("\n  4. Temporal Control Network...")
    # Create time periods (yearly)
    years = sorted(violence_data['date'].dt.year.unique())
    time_periods = [(pd.Timestamp(f'{y}-01-01'), pd.Timestamp(f'{y}-12-31')) 
                   for y in years]
    
    G_temporal = build_temporal_control_network(violence_data, time_periods)
    print(f"     ✓ {len(G_temporal.nodes())} nodes, {len(G_temporal.edges())} edges")
    visualize_temporal_control_network(G_temporal)

    return G_territorial, G_dyad, G_spatial, G_temporal

if __name__ == "__main__":
    networks = main()