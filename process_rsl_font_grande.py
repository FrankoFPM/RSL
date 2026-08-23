import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
import textwrap
import networkx as nx
from adjustText import adjust_text
from collections import defaultdict

# ----------------- DATA CLEANING FUNCTIONS -----------------

def clean_country(country_str):
    country = str(country_str).strip().replace('.', '').upper()
    country = ''.join([c for c in country if not c.isdigit()]).strip()
    
    mapping = {
        'PEOPLES R CHINA': 'CHINA',
        'PEOPLE R CHINA': 'CHINA',
        'PR CHINA': 'CHINA',
        'PEOPLES REPUBLIC OF CHINA': 'CHINA',
        'CHINESE ACADEMY OF SCIENCES': 'CHINA',
        'USA': 'USA',
        'US': 'USA',
        'UNITED STATES OF AMERICA': 'USA',
        'UNITED STATES': 'USA',
        'UNITED KINGDOM': 'UNITED KINGDOM',
        'UK': 'UNITED KINGDOM',
        'ENGLAND': 'UNITED KINGDOM',
        'SCOTLAND': 'UNITED KINGDOM',
        'WALES': 'UNITED KINGDOM',
        'NORTHERN IRELAND': 'UNITED KINGDOM',
        'SOUTH KOREA': 'SOUTH KOREA',
        'REPUBLIC OF KOREA': 'SOUTH KOREA',
        'KOREA': 'SOUTH KOREA',
    }
    
    if country in mapping:
        return mapping[country]
    for key, val in mapping.items():
        if key in country:
            return val
    return country

def clean_journal(journal_str):
    j = str(journal_str).strip().upper()
    j = ' '.join(j.split())
    
    mapping = {
        'IEEE TRANSACTIONS ON MOBILE COMPUTING': 'IEEE TRANSACTIONS ON MOBILE COMPUTING',
        'IEEE TRANS. MOB. COMPUT.': 'IEEE TRANSACTIONS ON MOBILE COMPUTING',
        'IEEE TRANS MOB COMPUT': 'IEEE TRANSACTIONS ON MOBILE COMPUTING',
        'IEEE INTERNET OF THINGS JOURNAL': 'IEEE INTERNET OF THINGS JOURNAL',
        'IEEE INTERNET OF THINGS J.': 'IEEE INTERNET OF THINGS JOURNAL',
        'IEEE ACCESS': 'IEEE ACCESS',
        'IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING': 'IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING',
        'IEEE TRANS. NETW. SCI. ENG.': 'IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING',
    }
    
    if j in mapping:
        return mapping[j]
    for key, val in mapping.items():
        if key in j:
            return val
    return j.title()

def clean_keyword(kw_str):
    k = str(kw_str).strip().lower()
    
    if k in ['large language models (llms)', 'large language model', 'llm', 'llms', 'large language models']:
        return 'Large language models'
    if k in ['quantization (signal)', 'quantization', 'quantizations', 'model quantization']:
        return 'Quantization'
    if k in ['computational modeling', 'computational model', 'computational models', 'computer simulation']:
        return 'Computational modeling'
    if k in ['edge computing', 'edge-computing']:
        return 'Edge computing'
    if k in ['knowledge distillation', 'knowledge-distillation', 'kd']:
        return 'Knowledge distillation'
    if k in ['model compression', 'model-compression']:
        return 'Model compression'
    if k in ['deep learning', 'deep-learning']:
        return 'Deep learning'
    if k in ['machine learning', 'machine-learning']:
        return 'Machine learning'
    if k in ['neural networks', 'artificial neural networks', 'neural network']:
        return 'Neural networks'
    
    return kw_str.strip().capitalize()

def extract_countries(c1_str, rp_str=None):
    addr_str = c1_str if pd.notna(c1_str) and str(c1_str).strip() else rp_str
    if pd.isna(addr_str):
        return []
    
    affiliations = str(addr_str).split(';')
    countries = []
    for aff in affiliations:
        aff = aff.strip()
        if not aff:
            continue
        parts = [p.strip() for p in aff.split(',') if p.strip()]
        if parts:
            last_part = parts[-1]
            country = clean_country(last_part)
            if country and len(country) < 30:
                countries.append(country)
    return list(set(countries))

def analyze_bradford(df):
    journal_counts = df['SO_Clean'].value_counts().reset_index()
    journal_counts.columns = ['Journal', 'Count']
    journal_counts['Rank'] = range(1, len(journal_counts) + 1)
    journal_counts['Cum_Count'] = journal_counts['Count'].cumsum()
    
    total_articles = len(df)
    zone_threshold = total_articles / 3.0
    
    zones = []
    current_cum = 0
    zone = 1
    for count in journal_counts['Count']:
        current_cum += count
        zones.append(zone)
        if zone == 1 and current_cum >= zone_threshold:
            zone = 2
        elif zone == 2 and current_cum >= 2 * zone_threshold:
            zone = 3
    journal_counts['Zone'] = zones
    return journal_counts

# ----------------- MAIN ANALYSIS ROUTINE -----------------

def run_analysis_font_grande():
    excel_file = 'ARTICULOS_UNIFICADOS_CRIBADO.xlsx'
    output_dir = 'graficos_fuente_grande'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading {excel_file}...")
    df = pd.read_excel(excel_file)
    
    # Fill missing values
    df['PY'] = df['PY'].fillna(0).astype(int)
    df['TC'] = df['TC'].fillna(0).astype(int)
    df['DE'] = df['DE'].fillna('')
    df['C1'] = df['C1'].fillna('')
    df['RP'] = df['RP'].fillna('')
    df['TI'] = df['TI'].fillna('Untitled')
    df['AU'] = df['AU'].fillna('Unknown')
    df['SO'] = df['SO'].fillna('Unknown')

    # Apply data cleaning
    df['SO_Clean'] = df['SO'].apply(clean_journal)
    df_filtered_py = df[df['PY'] > 0]

    # Global Style Setup for Matplotlib (Increased sizes for readability)
    plt.style.use('seaborn-v0_8-white' if 'seaborn-v0_8-white' in plt.style.available else 'default')
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['text.color'] = '#1e293b'
    plt.rcParams['axes.labelcolor'] = '#1e293b'
    plt.rcParams['xtick.color'] = '#475569'
    plt.rcParams['ytick.color'] = '#475569'
    
    # Base font size parameters
    plt.rcParams['font.size'] = 18
    plt.rcParams['axes.labelsize'] = 22
    plt.rcParams['xtick.labelsize'] = 18
    plt.rcParams['ytick.labelsize'] = 18
    plt.rcParams['legend.fontsize'] = 18
    
    # Curated Premium Color Palette
    color_navy = '#1e293b'
    color_blue = '#3b82f6'
    color_rose = '#f43f5e'
    color_teal = '#0f766e'
    color_orange = '#f97316'
    color_slate = '#64748b'

    # --- CHART 1: TEMPORAL EVOLUTION (image5.png) ---
    print("Processing Temporal Evolution -> image5.png")
    temporal = df_filtered_py.groupby('PY').agg(
        Articulos=('PY', 'count'),
        Promedio_Citas=('TC', 'mean')
    ).reset_index()
    
    fig, ax1 = plt.subplots(figsize=(12, 7.5), dpi=300)
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')
    
    bars = ax1.bar(temporal['PY'], temporal['Articulos'], color=color_navy, alpha=0.9, width=0.35, label='Artículos', edgecolor='none')
    ax1.set_xlabel('Año de Publicación', fontsize=22, labelpad=12, weight='bold')
    ax1.set_ylabel('Cantidad de Artículos', color=color_navy, fontsize=22, weight='bold')
    ax1.tick_params(axis='both', which='major', labelsize=18)
    ax1.tick_params(axis='y', labelcolor=color_navy)
    
    ax1.set_xticks(temporal['PY'])
    ax1.set_xticklabels(temporal['PY'].astype(int))
    ax1.set_xlim(temporal['PY'].min() - 0.5, temporal['PY'].max() + 0.5)
    ax1.grid(axis='y', linestyle='--', alpha=0.15, color='#cbd5e1')

    ax2 = ax1.twinx()
    ax2.set_facecolor('none')
    ax2.plot(temporal['PY'], temporal['Promedio_Citas'], color=color_rose, marker='o', markersize=10, linewidth=3, label='Citas Promedio')
    ax2.set_ylabel('Promedio de Citas (Impacto)', color=color_rose, fontsize=22, weight='bold', labelpad=12)
    ax2.tick_params(axis='y', labelcolor=color_rose, labelsize=18)
    
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 6),
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=16, weight='bold', color=color_navy)

    sns.despine(ax=ax1, right=False, top=True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'image5.png'), bbox_inches='tight')
    plt.close()
    print("Saved 'image5.png'")


    # --- CHART 2: KEYWORDS TREEMAP (image7.png) ---
    print("Processing Keywords Treemap -> image7.png")
    keywords_list = []
    for idx, row in df.iterrows():
        if row['DE']:
            kws = [clean_keyword(k) for k in str(row['DE']).split(';')]
            keywords_list.extend([k for k in kws if k])

    df_kw = pd.DataFrame(keywords_list, columns=['Keyword'])
    kw_counts = df_kw['Keyword'].value_counts().reset_index()
    kw_counts.columns = ['Keyword', 'Frecuencia']
    
    top_kws = kw_counts.head(12)
    colors = sns.color_palette("mako_r", n_colors=len(top_kws))
    
    plt.figure(figsize=(13, 9), dpi=300)
    plt.gcf().patch.set_facecolor('white')
    
    labels = []
    for idx, row in top_kws.iterrows():
        kw_wrapped = '\n'.join(textwrap.wrap(row['Keyword'], width=10))
        labels.append(f"{kw_wrapped}\n({row['Frecuencia']} u.)")

    squarify.plot(sizes=top_kws['Frecuencia'], label=labels, alpha=0.9, color=colors, edgecolor="white", linewidth=3, 
                  text_kwargs={'fontsize': 22, 'weight': 'bold', 'color': 'white'})
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'image7.png'), bbox_inches='tight')
    plt.close()
    print("Saved 'image7.png'")


    # --- CHART 3: COUNTRY PRODUCTIVITY (image9.png) ---
    print("Processing Country Productivity -> image9.png")
    country_counts = defaultdict(lambda: {'SCP': 0, 'MCP': 0})
    papers_with_country = 0
    collab_papers = 0
    
    for idx, row in df.iterrows():
        countries = extract_countries(row['C1'], row['RP'])
        if not countries:
            continue
        papers_with_country += 1
        if len(countries) == 1:
            country_counts[countries[0]]['SCP'] += 1
        else:
            collab_papers += 1
            for c in countries:
                country_counts[c]['MCP'] += 1

    country_data = []
    for c, stats in country_counts.items():
        country_data.append({
            'Country': c,
            'SCP': stats['SCP'],
            'MCP': stats['MCP'],
            'Total': stats['SCP'] + stats['MCP']
        })
    df_countries = pd.DataFrame(country_data)
    
    if not df_countries.empty:
        df_countries_top = df_countries.sort_values(by='Total', ascending=False).head(10)
        df_countries_plot = df_countries_top.iloc[::-1]
        
        plt.figure(figsize=(12, 8), dpi=300)
        plt.gcf().patch.set_facecolor('white')
        
        plt.barh(df_countries_plot['Country'], df_countries_plot['SCP'], color=color_teal, label='SCP (Coautoría Nacional)', height=0.55, alpha=0.9)
        plt.barh(df_countries_plot['Country'], df_countries_plot['MCP'], left=df_countries_plot['SCP'], color=color_orange, label='MCP (Coautoría Internacional)', height=0.55, alpha=0.9)
        
        plt.xlabel('Cantidad de Artículos', fontsize=22, weight='bold', labelpad=12)
        plt.ylabel('País de Afiliación', fontsize=22, weight='bold')
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        
        for idx, row in df_countries_plot.reset_index(drop=True).iterrows():
            total = row['Total']
            plt.annotate(f" {total}",
                         xy=(total, idx),
                         xytext=(5, 0),
                         textcoords="offset points",
                         ha='left', va='center', fontsize=16, weight='bold', color=color_navy)
            
        plt.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='none', fontsize=16)
        plt.grid(axis='x', linestyle='--', alpha=0.15, color='#cbd5e1')
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'image9.png'), bbox_inches='tight')
        plt.close()
        print("Saved 'image9.png'")
    else:
        print("Warning: No country data. Skipping country plot.")
        df_countries_top = pd.DataFrame(columns=['Country', 'SCP', 'MCP', 'Total'])


    # --- CHART 4: BRADFORD'S LAW (image8.png and rsl_ley_bradford.png) ---
    print("Processing Bradford's Law -> image8.png & rsl_ley_bradford.png")
    df_bradford = analyze_bradford(df)
    
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    ax.plot(df_bradford['Rank'], df_bradford['Cum_Count'], marker='s', markersize=8, color=color_navy, linewidth=2.5, label='Publicaciones Acumuladas')
    
    zone1_end = int(df_bradford[df_bradford['Zone'] == 1]['Rank'].max())
    zone2_end = int(df_bradford[df_bradford['Zone'] == 2]['Rank'].max())
    
    ax.axvline(x=zone1_end, color=color_rose, linestyle='--', linewidth=1.5, alpha=0.8)
    ax.axvline(x=zone2_end, color=color_blue, linestyle='--', linewidth=1.5, alpha=0.8)
    
    ax.axvspan(1, zone1_end, alpha=0.08, color='#f43f5e', label='Zona 1: Núcleo (Core)')
    ax.axvspan(zone1_end, zone2_end, alpha=0.08, color='#3b82f6', label='Zona 2: Conexión')
    ax.axvspan(zone2_end, len(df_bradford), alpha=0.08, color='#64748b', label='Zona 3: Periferia')
    
    ax.set_xscale('log')
    ax.set_xlabel('Rango de Revistas (Escala Logarítmica)', fontsize=22, weight='bold', labelpad=12)
    ax.set_ylabel('Artículos Acumulados', fontsize=22, weight='bold')
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.grid(True, which="both", ls="--", alpha=0.15, color='#cbd5e1')
    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='none', fontsize=16)
    sns.despine(left=True, bottom=True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'image8.png'), bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'rsl_ley_bradford.png'), bbox_inches='tight')
    plt.close()
    print("Saved 'image8.png' and 'rsl_ley_bradford.png'")


    # --- NETWORK PREPARATION ---
    print("Building Co-occurrence Graph...")
    top_25_kws = kw_counts.head(25)
    G = nx.Graph()
    for _, row in top_25_kws.iterrows():
        G.add_node(row['Keyword'], size=row['Frecuencia'])
        
    for kws_str in df['DE']:
        if not kws_str:
            continue
        kws = list(set([clean_keyword(k) for k in str(kws_str).split(';') if k.strip()]))
        kws = [k for k in kws if k in G.nodes]
        for i in range(len(kws)):
            for j in range(i+1, len(kws)):
                if G.has_edge(kws[i], kws[j]):
                    G[kws[i]][kws[j]]['weight'] += 1
                else:
                    G.add_edge(kws[i], kws[j], weight=1)
                    
    isolates = list(nx.isolates(G))
    G.remove_nodes_from(isolates)


    # --- CHART 5: KEYWORD CO-OCCURRENCE NETWORK (image4.png) ---
    if len(G.nodes) > 0:
        print("Drawing Keyword Co-occurrence Network -> image4.png")
        plt.figure(figsize=(14, 12), dpi=300)
        plt.gcf().patch.set_facecolor('white')
        
        pos = nx.spring_layout(G, k=1.8, iterations=120, seed=42)
        
        node_sizes = [G.nodes[n]['size'] * 260 for n in G.nodes]
        
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        max_w = max(weights) if weights else 1
        edge_widths = [1.2 + w / max_w * 7 for w in weights]
        
        degrees = dict(G.degree())
        node_colors = [degrees[n] for n in G.nodes]
        
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, cmap=plt.cm.viridis, alpha=0.9, linewidths=1.5, edgecolors='white')
        nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='#64748b', alpha=0.8)
        
        net_texts = [plt.text(x, y, s=node, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'),
                               horizontalalignment='center', fontsize=20, weight='bold', color=color_navy)
                     for node, (x, y) in pos.items()]
        adjust_text(net_texts, expand=(1.4, 1.8),
                    arrowprops=dict(arrowstyle='-', color=color_slate, lw=0.6, alpha=0.5))
            
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'image4.png'), bbox_inches='tight')
        plt.close()
        print("Saved 'image4.png'")
    else:
        print("Warning: Network is empty. Skipping co-occurrence network plot.")


    # --- CHART 6: STRATEGIC THEMATIC MAP (image6.png) ---
    if len(G.nodes) > 0:
        print("Processing Thematic Map -> image6.png")
        centrality = {}
        density = {}
        for node in G.nodes:
            c_val = sum(G[node][neighbor]['weight'] for neighbor in G.neighbors(node))
            centrality[node] = c_val
            
            neighbors = list(G.neighbors(node))
            if len(neighbors) < 2:
                d_val = 0.0
            else:
                subgraph = G.subgraph(neighbors)
                subgraph_edges = subgraph.edges(data=True)
                if len(subgraph_edges) == 0:
                    d_val = 0.0
                else:
                    d_val = sum(data.get('weight', 1.0) for _, _, data in subgraph_edges) / len(subgraph_edges)
            density[node] = d_val

        df_thematic = pd.DataFrame([
            {'Keyword': node, 'Centrality': float(centrality[node]), 'Density': float(density[node]), 'Frequency': int(G.nodes[node]['size'])}
            for node in G.nodes
        ])
        
        fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        ax.scatter(df_thematic['Centrality'], df_thematic['Density'], s=df_thematic['Frequency']*45, color=color_rose, alpha=0.75, edgecolors='white', linewidths=1.5)
        
        # Etiquetar solo los temas mas importantes (top 10 por frecuencia) para evitar solapamiento
        top_labels = df_thematic.nlargest(10, 'Frequency')
        theme_texts = [ax.text(row['Centrality'], row['Density'], row['Keyword'], fontsize=16, weight='bold', color=color_navy)
                       for _, row in top_labels.iterrows()]

        med_c = float(df_thematic['Centrality'].median())
        med_d = float(df_thematic['Density'].median())
        
        ax.axvline(x=med_c, color=color_slate, linestyle='--', linewidth=1.5, alpha=0.6)
        ax.axhline(y=med_d, color=color_slate, linestyle='--', linewidth=1.5, alpha=0.6)

        ax.margins(0.22)  # holgura para separar puntos del borde y dar espacio a rotulos de cuadrante
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        quad_texts = [
            ax.text(xlim[1] - (xlim[1]-med_c)*0.05, ylim[1] - (ylim[1]-med_d)*0.05, 'TEMAS MOTOR\n(Motor Themes)', ha='right', va='top', fontsize=15, weight='bold', color='#16a34a'),
            ax.text(xlim[0] + (med_c-xlim[0])*0.05, ylim[1] - (ylim[1]-med_d)*0.05, 'TEMAS NICHO\n(Niche Themes)', ha='left', va='top', fontsize=15, weight='bold', color='#4f46e5'),
            ax.text(xlim[0] + (med_c-xlim[0])*0.05, ylim[0] + (med_d-ylim[0])*0.05, 'TEMAS EMERGENTES\nO EN DECLIVE', ha='left', va='bottom', fontsize=15, weight='bold', color='#dc2626'),
            ax.text(xlim[1] - (xlim[1]-med_c)*0.05, ylim[0] + (med_d-ylim[0])*0.05, 'TEMAS BÁSICOS\nY TRANSVERSALES', ha='right', va='bottom', fontsize=15, weight='bold', color='#ca8a04'),
        ]

        # Repeler etiquetas de temas, evitando tambien los rotulos de cuadrante
        adjust_text(theme_texts, ax=ax, objects=quad_texts, expand=(1.4, 1.8),
                    arrowprops=dict(arrowstyle='-', color=color_slate, lw=0.7, alpha=0.6))

        ax.set_xlabel('Centralidad (Relevancia / Conexión Externa)', fontsize=22, weight='bold', labelpad=12)
        ax.set_ylabel('Densidad (Desarrollo / Cohesión Interna)', fontsize=22, weight='bold', labelpad=12)
        ax.tick_params(axis='both', which='major', labelsize=18)
        ax.grid(True, linestyle='--', alpha=0.1, color='#cbd5e1')
        sns.despine(left=True, bottom=True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'image6.png'), bbox_inches='tight')
        plt.close()
        print("Saved 'image6.png'")
    else:
        print("Warning: Network is empty. Skipping thematic map plot.")


    # --- CHART 7: SANKEY / THREE FIELDS PLOT (image11.png) ---
    print("Processing Three-Fields Plot (Sankey) -> image11.png")
    top_countries_list = df_countries.sort_values(by='Total', ascending=False).head(8)['Country'].tolist()
    top_keywords_list = kw_counts.head(10)['Keyword'].tolist()
    top_journals_list = df['SO_Clean'].value_counts().head(8).index.tolist()
    
    top_countries_set = set(top_countries_list)
    top_keywords_set = set(top_keywords_list)
    top_journals_set = set(top_journals_list)
    
    country_keyword_links = defaultdict(int)
    keyword_journal_links = defaultdict(int)
    
    for _, row in df.iterrows():
        journal = str(row['SO_Clean']).strip()
        if journal not in top_journals_set:
            continue
            
        countries = extract_countries(row['C1'], row['RP'])
        countries = [c for c in countries if c in top_countries_set]
        
        kws = [clean_keyword(k) for k in str(row['DE']).split(';') if k.strip()]
        kws = [k for k in kws if k in top_keywords_set]
        
        for c in countries:
            for k in kws:
                country_keyword_links[(c, k)] += 1
                
        for k in kws:
            keyword_journal_links[(k, journal)] += 1
            
    sankey_nodes = list(top_countries_list) + list(top_keywords_list) + list(top_journals_list)
    node_to_idx = {name: idx for idx, name in enumerate(sankey_nodes)}
    
    # Wrapped labels for the diagram nodes to avoid squishing
    sankey_labels = []
    for name in sankey_nodes:
        if len(name) > 20:
            sankey_labels.append("<br>".join(textwrap.wrap(name, width=20)))
        else:
            sankey_labels.append(name)

    sankey_links = []
    for (c, k), val in country_keyword_links.items():
        sankey_links.append({
            'source': node_to_idx[c],
            'target': node_to_idx[k],
            'value': val
        })
    for (k, j), val in keyword_journal_links.items():
        sankey_links.append({
            'source': node_to_idx[k],
            'target': node_to_idx[j],
            'value': val
        })
        
    # Export Sankey Diagram as static PNG with large fonts and no title
    try:
        import plotly.graph_objects as go
        sankey_node_colors = []
        for idx, name in enumerate(sankey_nodes):
            if idx < len(top_countries_list):
                sankey_node_colors.append('#14b8a6')
            elif idx < len(top_countries_list) + len(top_keywords_list):
                sankey_node_colors.append('#8b5cf6')
            else:
                sankey_node_colors.append('#ec4899')

        fig_s = go.Figure(data=[go.Sankey(
            node = dict(
              pad = 30, # Increased vertical padding between nodes
              thickness = 25,
              line = dict(color = "rgba(0,0,0,0.3)", width = 0.5),
              label = sankey_labels, # Use wrapped labels to prevent squishing
              color = sankey_node_colors
            ),
            link = dict(
              source = [l['source'] for l in sankey_links],
              target = [l['target'] for l in sankey_links],
              value = [l['value'] for l in sankey_links],
              color = 'rgba(100, 116, 139, 0.15)'
            )
        )])

        fig_s.update_layout(
            font_size=24,  # Optimized large font size to prevent overlapping
            font_family="Arial",
            width=1800,    # Increased width to separate columns
            height=1000,   # Increased height to give nodes more vertical space
            margin=dict(t=20, b=20, l=20, r=20)
        )
        fig_s.write_image(os.path.join(output_dir, "image11.png"), scale=3)
        print("Saved 'image11.png'")
    except Exception as e:
        print(f"Warning: Could not export Sankey image: {e}")

    print("All large font graphics successfully generated!")

if __name__ == '__main__':
    run_analysis_font_grande()
