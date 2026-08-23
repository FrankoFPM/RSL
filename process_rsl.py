import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
import json
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

def run_analysis(no_title=False, output_dir='.'):
    import os
    if output_dir != '.':
        os.makedirs(output_dir, exist_ok=True)
    excel_file = 'ARTICULOS_UNIFICADOS_CRIBADO.xlsx'
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

    # Global Style Setup for Matplotlib
    plt.style.use('seaborn-v0_8-white' if 'seaborn-v0_8-white' in plt.style.available else 'default')
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['text.color'] = '#1e293b'
    plt.rcParams['axes.labelcolor'] = '#1e293b'
    plt.rcParams['xtick.color'] = '#475569'
    plt.rcParams['ytick.color'] = '#475569'
    
    # Curated Premium Color Palette
    color_navy = '#1e293b'
    color_blue = '#3b82f6'
    color_rose = '#f43f5e'
    color_teal = '#0f766e'
    color_orange = '#f97316'
    color_slate = '#64748b'

    # --- CHART 1: TEMPORAL EVOLUTION ---
    print("Processing Temporal Evolution...")
    temporal = df_filtered_py.groupby('PY').agg(
        Articulos=('PY', 'count'),
        Promedio_Citas=('TC', 'mean')
    ).reset_index()
    
    fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=300)
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')
    
    bars = ax1.bar(temporal['PY'], temporal['Articulos'], color=color_navy, alpha=0.9, width=0.35, label='Artículos', edgecolor='none')
    ax1.set_xlabel('Año de Publicación', fontsize=11, labelpad=12, weight='bold')
    ax1.set_ylabel('Cantidad de Artículos', color=color_navy, fontsize=11, weight='bold')
    ax1.tick_params(axis='y', labelcolor=color_navy)
    
    ax1.set_xticks(temporal['PY'])
    ax1.set_xticklabels(temporal['PY'].astype(int))
    ax1.set_xlim(temporal['PY'].min() - 0.5, temporal['PY'].max() + 0.5)
    ax1.grid(axis='y', linestyle='--', alpha=0.15, color='#cbd5e1')

    ax2 = ax1.twinx()
    ax2.set_facecolor('none')
    ax2.plot(temporal['PY'], temporal['Promedio_Citas'], color=color_rose, marker='o', markersize=8, linewidth=3, label='Citas Promedio')
    ax2.set_ylabel('Promedio de Citas (Impacto)', color=color_rose, fontsize=11, weight='bold', labelpad=12)
    ax2.tick_params(axis='y', labelcolor=color_rose)
    
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5),
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=9, weight='bold', color=color_navy)

    if not no_title:
        plt.title('Producción Científica Anual e Impacto de Citación', fontsize=13, pad=20, weight='bold', color=color_navy)
    sns.despine(ax=ax1, right=False, top=True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rsl_evolucion_temporal.png'), bbox_inches='tight')
    plt.close()
    print("Saved 'rsl_evolucion_temporal.png'")


    # --- CHART 2: KEYWORDS TREEMAP ---
    print("Processing Keywords Treemap...")
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
    
    plt.figure(figsize=(12, 7), dpi=300)
    plt.gcf().patch.set_facecolor('white')
    
    labels = []
    for idx, row in top_kws.iterrows():
        kw_wrapped = '\n'.join(textwrap.wrap(row['Keyword'], width=15))
        labels.append(f"{kw_wrapped}\n({row['Frecuencia']} u.)")

    squarify.plot(sizes=top_kws['Frecuencia'], label=labels, alpha=0.9, color=colors, edgecolor="white", linewidth=3, 
                  text_kwargs={'fontsize': 14, 'weight': 'bold', 'color': 'white'})
    
    if not no_title:
        plt.title('Análisis Temático: Distribución de Palabras Clave del Autor (DE)', fontsize=14, pad=20, weight='bold', color=color_navy)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rsl_treemap_keywords.png'), bbox_inches='tight')
    plt.close()
    print("Saved 'rsl_treemap_keywords.png'")


    # --- CHART 3: COUNTRY PRODUCTIVITY (SCP vs MCP) ---
    print("Processing Country Productivity...")
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
        
        plt.figure(figsize=(10, 6), dpi=300)
        plt.gcf().patch.set_facecolor('white')
        
        plt.barh(df_countries_plot['Country'], df_countries_plot['SCP'], color=color_teal, label='SCP (Coautoría Nacional)', height=0.55, alpha=0.9)
        plt.barh(df_countries_plot['Country'], df_countries_plot['MCP'], left=df_countries_plot['SCP'], color=color_orange, label='MCP (Coautoría Internacional)', height=0.55, alpha=0.9)
        
        if not no_title:
            plt.title('Top 10 Países más Productivos en la RSL (SCP vs MCP)', fontsize=13, pad=20, weight='bold', color=color_navy)
        plt.xlabel('Cantidad de Artículos', fontsize=11, weight='bold', labelpad=12)
        plt.ylabel('País de Afiliación', fontsize=11, weight='bold')
        
        for idx, row in df_countries_plot.reset_index(drop=True).iterrows():
            total = row['Total']
            plt.annotate(f" {total}",
                         xy=(total, idx),
                         xytext=(5, 0),
                         textcoords="offset points",
                         ha='left', va='center', fontsize=9, weight='bold', color=color_navy)
            
        plt.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='none')
        plt.grid(axis='x', linestyle='--', alpha=0.15, color='#cbd5e1')
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'rsl_paises_productividad.png'), bbox_inches='tight')
        plt.close()
        print("Saved 'rsl_paises_productividad.png'")
    else:
        print("Warning: No country data. Skipping country plot.")
        df_countries_top = pd.DataFrame(columns=['Country', 'SCP', 'MCP', 'Total'])


    # --- CHART 4: BRADFORD'S LAW ---
    print("Processing Bradford's Law...")
    df_bradford = analyze_bradford(df)
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    ax.plot(df_bradford['Rank'], df_bradford['Cum_Count'], marker='s', markersize=6, color=color_navy, linewidth=2.5, label='Publicaciones Acumuladas')
    
    zone1_end = int(df_bradford[df_bradford['Zone'] == 1]['Rank'].max())
    zone2_end = int(df_bradford[df_bradford['Zone'] == 2]['Rank'].max())
    
    ax.axvline(x=zone1_end, color=color_rose, linestyle='--', linewidth=1.5, alpha=0.8)
    ax.axvline(x=zone2_end, color=color_blue, linestyle='--', linewidth=1.5, alpha=0.8)
    
    ax.axvspan(1, zone1_end, alpha=0.08, color='#f43f5e', label='Zona 1: Núcleo (Core)')
    ax.axvspan(zone1_end, zone2_end, alpha=0.08, color='#3b82f6', label='Zona 2: Conexión')
    ax.axvspan(zone2_end, len(df_bradford), alpha=0.08, color='#64748b', label='Zona 3: Periferia')
    
    ax.set_xscale('log')
    ax.set_xlabel('Rango de Revistas (Escala Logarítmica)', fontsize=11, weight='bold', labelpad=12)
    ax.set_ylabel('Artículos Acumulados', fontsize=11, weight='bold')
    if not no_title:
        ax.set_title('Ley de Bradford: Zonas de Publicación e Influencia', fontsize=13, pad=20, weight='bold', color=color_navy)
    ax.grid(True, which="both", ls="--", alpha=0.15, color='#cbd5e1')
    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='none')
    sns.despine(left=True, bottom=True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rsl_ley_bradford.png'), bbox_inches='tight')
    plt.close()
    print("Saved 'rsl_ley_bradford.png'")


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


    # --- CHART 5: KEYWORD CO-OCCURRENCE NETWORK ---
    if len(G.nodes) > 0:
        print("Drawing Keyword Co-occurrence Network...")
        plt.figure(figsize=(12, 10), dpi=300)
        plt.gcf().patch.set_facecolor('white')
        
        pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
        
        node_sizes = [G.nodes[n]['size'] * 150 for n in G.nodes]
        
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        max_w = max(weights) if weights else 1
        edge_widths = [1.2 + w / max_w * 7 for w in weights]
        
        degrees = dict(G.degree())
        node_colors = [degrees[n] for n in G.nodes]
        
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, cmap=plt.cm.viridis, alpha=0.9, linewidths=1.5, edgecolors='white')
        nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='#64748b', alpha=0.8)
        
        net_texts = [plt.text(x, y, s=node, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'),
                              horizontalalignment='center', fontsize=13, weight='bold', color=color_navy)
                     for node, (x, y) in pos.items()]
        adjust_text(net_texts, expand=(1.2, 1.5),
                    arrowprops=dict(arrowstyle='-', color=color_slate, lw=0.6, alpha=0.5))
            
        if not no_title:
            plt.title('Red de Co-ocurrencia de Palabras Clave (Top Autores)', fontsize=14, pad=25, weight='bold', color=color_navy)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'rsl_red_coocurrencia.png'), bbox_inches='tight')
        plt.close()
        print("Saved 'rsl_red_coocurrencia.png'")
    else:
        print("Warning: Network is empty. Skipping co-occurrence network plot.")


    # --- CHART 6: STRATEGIC THEMATIC MAP ---
    if len(G.nodes) > 0:
        print("Processing Thematic Map...")
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
        
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        ax.scatter(df_thematic['Centrality'], df_thematic['Density'], s=df_thematic['Frequency']*25, color=color_rose, alpha=0.75, edgecolors='white', linewidths=1.5)
        
        # Etiquetar solo los temas mas importantes (top 10 por frecuencia) para evitar solapamiento
        top_labels = df_thematic.nlargest(10, 'Frequency')
        theme_texts = [ax.text(row['Centrality'], row['Density'], row['Keyword'], fontsize=10, weight='bold', color=color_navy)
                       for _, row in top_labels.iterrows()]

        med_c = float(df_thematic['Centrality'].median())
        med_d = float(df_thematic['Density'].median())
        
        ax.axvline(x=med_c, color=color_slate, linestyle='--', linewidth=1.5, alpha=0.6)
        ax.axhline(y=med_d, color=color_slate, linestyle='--', linewidth=1.5, alpha=0.6)

        ax.margins(0.22)  # holgura para separar puntos del borde y dar espacio a rotulos de cuadrante
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        quad_texts = [
            ax.text(xlim[1] - (xlim[1]-med_c)*0.05, ylim[1] - (ylim[1]-med_d)*0.05, 'TEMAS MOTOR\n(Motor Themes)', ha='right', va='top', fontsize=10, weight='bold', color='#16a34a'),
            ax.text(xlim[0] + (med_c-xlim[0])*0.05, ylim[1] - (ylim[1]-med_d)*0.05, 'TEMAS NICHO\n(Niche Themes)', ha='left', va='top', fontsize=10, weight='bold', color='#4f46e5'),
            ax.text(xlim[0] + (med_c-xlim[0])*0.05, ylim[0] + (med_d-ylim[0])*0.05, 'TEMAS EMERGENTES\nO EN DECLIVE', ha='left', va='bottom', fontsize=10, weight='bold', color='#dc2626'),
            ax.text(xlim[1] - (xlim[1]-med_c)*0.05, ylim[0] + (med_d-ylim[0])*0.05, 'TEMAS BÁSICOS\nY TRANSVERSALES', ha='right', va='bottom', fontsize=10, weight='bold', color='#ca8a04'),
        ]

        # Repeler etiquetas de temas, evitando tambien los rotulos de cuadrante
        adjust_text(theme_texts, ax=ax, objects=quad_texts, expand=(1.3, 1.6),
                    arrowprops=dict(arrowstyle='-', color=color_slate, lw=0.7, alpha=0.6))

        ax.set_xlabel('Centralidad (Relevancia / Conexión Externa)', fontsize=11, weight='bold', labelpad=12)
        ax.set_ylabel('Densidad (Desarrollo / Cohesión Interna)', fontsize=11, weight='bold', labelpad=12)
        if not no_title:
            ax.set_title('Mapa Temático: Clasificación Estratégica de Temas en la RSL', fontsize=13, pad=20, weight='bold', color=color_navy)
        ax.grid(True, linestyle='--', alpha=0.1, color='#cbd5e1')
        sns.despine(left=True, bottom=True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'rsl_mapa_tematico.png'), bbox_inches='tight')
        plt.close()
        print("Saved 'rsl_mapa_tematico.png'")
    else:
        print("Warning: Network is empty. Skipping thematic map plot.")
        df_thematic = pd.DataFrame(columns=['Keyword', 'Centrality', 'Density', 'Frequency'])
        med_c = 0.0
        med_d = 0.0


    # --- CHART 7: SANKEY / THREE FIELDS PLOT ---
    print("Processing Three-Fields Plot (Sankey)...")
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
        
    sankey_data = {
        'nodes': [{'name': n} for n in sankey_nodes],
        'links': sankey_links,
        'country_count': len(top_countries_list),
        'keyword_count': len(top_keywords_list),
        'journal_count': len(top_journals_list)
    }

    # Export Sankey Diagram as static PNG
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
              pad = 15,
              thickness = 20,
              line = dict(color = "rgba(0,0,0,0.3)", width = 0.5),
              label = sankey_nodes,
              color = sankey_node_colors
            ),
            link = dict(
              source = [l['source'] for l in sankey_links],
              target = [l['target'] for l in sankey_links],
              value = [l['value'] for l in sankey_links],
              color = 'rgba(100, 116, 139, 0.15)'
            )
        )])

        layout_params = dict(
            font_size=16,
            font_family="Arial",
            width=1200,
            height=700
        )
        if not no_title:
            layout_params['title_text'] = "Diagrama de Tres Campos: Países ➔ Palabras Clave ➔ Revistas"
        else:
            layout_params['margin'] = dict(t=10, b=10, l=10, r=10)
        fig_s.update_layout(**layout_params)
        fig_s.write_image(os.path.join(output_dir, "rsl_tres_campos.png"), scale=3)
        print("Saved 'rsl_tres_campos.png'")
    except Exception as e:
        print(f"Warning: Could not export Sankey image: {e}")

    if no_title:
        print("Skipping HTML Dashboard generation as no_title is True.")
        return

    # --- GENERATING INTERACTIVE HTML DASHBOARD ---
    print("Generating HTML Dashboard...")
    
    total_articles = len(df)
    years_range = f"{df_filtered_py['PY'].min()} - {df_filtered_py['PY'].max()}" if not df_filtered_py.empty else "N/A"
    total_citations = int(df['TC'].sum())
    avg_citations = round(float(df['TC'].mean()), 2) if total_articles > 0 else 0.0
    collaboration_rate = round((collab_papers / papers_with_country * 100), 1) if papers_with_country > 0 else 0.0
    top_country = df_countries.sort_values(by='Total', ascending=False).iloc[0]['Country'] if not df_countries.empty else "N/A"
    
    dashboard_data = {
        'kpis': {
            'totalArticles': total_articles,
            'yearsRange': years_range,
            'totalCitations': total_citations,
            'avgCitations': avg_citations,
            'collaborationRate': f"{collaboration_rate}%",
            'topCountry': top_country
        },
        'temporal': temporal.to_dict(orient='records'),
        'keywords': top_kws.to_dict(orient='records'),
        'countries': df_countries.sort_values(by='Total', ascending=False).head(15).to_dict(orient='records'),
        'bradford': df_bradford[['Journal', 'Rank', 'Cum_Count', 'Zone']].to_dict(orient='records'),
        'bradford_zone1_end': zone1_end,
        'bradford_zone2_end': zone2_end,
        'thematic': df_thematic.to_dict(orient='records') if 'df_thematic' in locals() else [],
        'thematic_median_c': float(med_c) if 'med_c' in locals() else 0.0,
        'thematic_median_d': float(med_d) if 'med_d' in locals() else 0.0,
        'sankey': sankey_data,
        'articles': [
            {
                'title': str(row['TI']).strip(),
                'authors': str(row['AU']).strip(),
                'journal': str(row['SO_Clean']).strip(),
                'year': int(row['PY']),
                'citations': int(row['TC']),
                'keywords': str(row['DE']).strip()
            } for _, row in df.iterrows()
        ]
    }
    
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Analítico de la RSL - Q1/Q2 Grade</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #151c2c;
            --border-color: #222e45;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent-primary: #8b5cf6;
            --accent-secondary: #ec4899;
            --accent-teal: #14b8a6;
            --accent-amber: #f59e0b;
            --accent-blue: #3b82f6;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            padding: 2rem;
            min-height: 100vh;
        }}
        
        header {{
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        
        h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #a78bfa, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: rgba(0,0,0,0);
        }}
        
        .subtitle {{
            color: var(--text-muted);
            margin-top: 0.3rem;
            font-size: 1rem;
        }}

        .file-info {{
            font-size: 0.85rem;
            color: var(--text-muted);
            background: rgba(255,255,255,0.03);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}

        .section-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-main);
            margin-top: 3rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .section-title span {{
            background: rgba(139, 92, 246, 0.1);
            color: var(--accent-primary);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 700;
        }}
        
        /* KPI Grid */
        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }}
        
        .kpi-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }}
        
        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
        }}
        
        .kpi-card.purple::before {{ background: var(--accent-primary); }}
        .kpi-card.pink::before {{ background: var(--accent-secondary); }}
        .kpi-card.teal::before {{ background: var(--accent-teal); }}
        .kpi-card.amber::before {{ background: var(--accent-amber); }}
        
        .kpi-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
            border-color: rgba(255,255,255,0.1);
        }}
        
        .kpi-title {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        
        .kpi-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-main);
        }}
        
        .kpi-footer {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
            display: flex;
            justify-content: space-between;
        }}
        
        /* Charts Grid */
        .charts-container {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }}
        
        .chart-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }}
        
        .col-12 {{ grid-column: span 12; }}
        .col-6 {{ grid-column: span 6; }}
        
        @media (max-width: 1024px) {{
            .col-6 {{ grid-column: span 12; }}
        }}
        
        .chart-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }}

        .chart-title .title-text {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .chart-title .badge-q {{
            font-size: 0.7rem;
            background: rgba(20, 184, 166, 0.1);
            color: var(--accent-teal);
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        
        .plotly-chart {{
            width: 100%;
            height: 400px;
        }}
        
        /* Article Table Section */
        .table-section {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            margin-top: 3rem;
        }}
        
        .table-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        
        .search-container {{
            position: relative;
            flex-grow: 1;
            max-width: 400px;
        }}
        
        .search-input {{
            width: 100%;
            background-color: rgba(255,255,255,0.05);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.6rem 1rem;
            color: var(--text-main);
            outline: none;
            transition: all 0.3s ease;
        }}
        
        .search-input:focus {{
            border-color: var(--accent-primary);
            background-color: rgba(255,255,255,0.08);
            box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            max-height: 500px;
            overflow-y: auto;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
        }}
        
        th {{
            background-color: rgba(255,255,255,0.03);
            color: var(--text-muted);
            font-weight: 600;
            padding: 0.8rem 1rem;
            position: sticky;
            top: 0;
            border-bottom: 2px solid var(--border-color);
            z-index: 10;
        }}
        
        td {{
            padding: 0.8rem 1rem;
            border-bottom: 1px solid var(--border-color);
            vertical-align: middle;
        }}
        
        tr:hover {{
            background-color: rgba(255,255,255,0.01);
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .badge-year {{
            background-color: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }}
        
        .badge-citations {{
            background-color: rgba(236, 72, 153, 0.15);
            color: #f472b6;
            border: 1px solid rgba(236, 72, 153, 0.3);
        }}

        .article-title {{
            font-weight: 500;
            color: var(--text-main);
            max-width: 450px;
            white-space: normal;
            word-wrap: break-word;
        }}

        .article-authors {{
            color: var(--text-muted);
            font-size: 0.85rem;
            max-width: 250px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
    </style>
</head>
<body>

    <header>
        <div>
            <h1>Dashboard de RSL (Nivel Q1/Q2)</h1>
            <div class="subtitle">Análisis Estructural, Redes Temáticas y Colaboración Científica</div>
        </div>
        <div class="file-info">
            Origen: <strong>{excel_file}</strong>
        </div>
    </header>

    <!-- KPI Row -->
    <div class="kpi-container">
        <div class="kpi-card purple">
            <div class="kpi-title">Total Artículos</div>
            <div class="kpi-value" id="kpi-total-articles">-</div>
            <div class="kpi-footer">
                <span>Rango: <strong id="kpi-years-range">-</strong></span>
            </div>
        </div>
        <div class="kpi-card pink">
            <div class="kpi-title">Total Citas</div>
            <div class="kpi-value" id="kpi-total-citations">-</div>
            <div class="kpi-footer">
                <span>Promedio: <strong id="kpi-avg-citations">-</strong> por paper</span>
            </div>
        </div>
        <div class="kpi-card teal">
            <div class="kpi-title">Coautoría Internacional</div>
            <div class="kpi-value" id="kpi-collab-rate">-</div>
            <div class="kpi-footer">
                <span>Tasa de colaboración MCP</span>
            </div>
        </div>
        <div class="kpi-card amber">
            <div class="kpi-title">País Más Productivo</div>
            <div class="kpi-value" id="kpi-top-country" style="font-size: 1.6rem; padding-top: 0.4rem;">-</div>
            <div class="kpi-footer">
                <span>Líder en publicaciones</span>
            </div>
        </div>
    </div>

    <!-- SECCIÓN 1: PRODUCCIÓN E IMPACTO ESTRUCTURAL -->
    <div class="section-title">
        <span>Sección 1</span> Producción e Impacto Estructural de la Literatura
    </div>
    
    <div class="charts-container">
        <div class="chart-card col-12">
            <div class="chart-title">
                <div class="title-text">
                    <span>1. Evolución Temporal de Producción e Impacto de Citas</span>
                    <span class="badge-q">Descriptivo Clave</span>
                </div>
                <span class="subtitle" style="font-size: 0.8rem;">Volumen de artículos publicados vs promedio anual de citación</span>
            </div>
            <div id="chart-temporal" class="plotly-chart"></div>
        </div>

        <div class="chart-card col-6">
            <div class="chart-title">
                <div class="title-text">
                    <span>2. Ley de Bradford: Zonas de Publicación</span>
                    <span class="badge-q">Q1/Q2 Estructural</span>
                </div>
                <span class="subtitle" style="font-size: 0.8rem;">Distribución acumulada en revistas. Las líneas punteadas muestran límites de Zona 1 y 2</span>
            </div>
            <div id="chart-bradford" class="plotly-chart"></div>
        </div>

        <div class="chart-card col-6">
            <div class="chart-title">
                <div class="title-text">
                    <span>3. Colaboración Internacional de Países (SCP vs MCP)</span>
                    <span class="badge-q">Q1/Q2 Colaboración</span>
                </div>
                <span class="subtitle" style="font-size: 0.8rem;">Top 10 Países ordenados por productividad. Compara artículos nacionales vs internacionales</span>
            </div>
            <div id="chart-countries" class="plotly-chart"></div>
        </div>
    </div>

    <!-- SECCIÓN 2: ESTRUCTURA CONCEPTUAL Y TEMAS -->
    <div class="section-title">
        <span>Sección 2</span> Estructura Conceptual y Mapa Estratégico de Temas
    </div>

    <div class="charts-container">
        <div class="chart-card col-6">
            <div class="chart-title">
                <div class="title-text">
                    <span>4. Análisis Temático: Distribución de Palabras Clave (Treemap)</span>
                    <span class="badge-q">Descriptivo Temático</span>
                </div>
                <span class="subtitle" style="font-size: 0.8rem;">Proporción y volumen de las 12 palabras clave del autor más dominantes</span>
            </div>
            <div id="chart-treemap" class="plotly-chart"></div>
        </div>

        <div class="chart-card col-6">
            <div class="chart-title">
                <div class="title-text">
                    <span>5. Mapa Temático: Clasificación de Temas (Centralidad vs Densidad)</span>
                    <span class="badge-q">Q1/Q2 Estratégico</span>
                </div>
                <span class="subtitle" style="font-size: 0.8rem;">Clasificación de palabras clave en los 4 cuadrantes estratégicos de Callon</span>
            </div>
            <div id="chart-thematic" class="plotly-chart"></div>
        </div>
    </div>

    <!-- SECCIÓN 3: DIAGRAMA DE TRES CAMPOS -->
    <div class="section-title">
        <span>Sección 3</span> Diagrama de Tres Campos (Three-Fields Plot)
    </div>

    <div class="charts-container">
        <div class="chart-card col-12">
            <div class="chart-title">
                <div class="title-text">
                    <span>6. Flujo de Investigación: Países ➔ Palabras Clave ➔ Revistas</span>
                    <span class="badge-q">Q1/Q2 Integrador</span>
                </div>
                <span class="subtitle" style="font-size: 0.8rem;">Muestra visualmente la interacción entre países de origen, temas estudiados y revistas publicadas</span>
            </div>
            <div id="chart-sankey" class="plotly-chart" style="height: 500px;"></div>
        </div>
    </div>

    <!-- Table Section -->
    <div class="table-section">
        <div class="table-header">
            <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 600;">Listado de Artículos Analizados</h2>
            <div class="search-container">
                <input type="text" id="table-search" class="search-input" placeholder="Buscar por título, autor o palabra clave...">
            </div>
        </div>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th style="width: 50px;">#</th>
                        <th>Título</th>
                        <th>Autores</th>
                        <th>Revista / Origen</th>
                        <th style="width: 80px; text-align: center;">Año</th>
                        <th style="width: 80px; text-align: center;">Citas</th>
                    </tr>
                </thead>
                <tbody id="articles-table-body">
                    <!-- Dynamic Rows -->
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Inject Data
        const rslData = {json.dumps(dashboard_data, indent=4)};
        
        // Populate KPIs
        document.getElementById('kpi-total-articles').innerText = rslData.kpis.totalArticles;
        document.getElementById('kpi-years-range').innerText = rslData.kpis.yearsRange;
        document.getElementById('kpi-total-citations').innerText = rslData.kpis.totalCitations;
        document.getElementById('kpi-avg-citations').innerText = rslData.kpis.avgCitations;
        document.getElementById('kpi-collab-rate').innerText = rslData.kpis.collaborationRate;
        document.getElementById('kpi-top-country').innerText = rslData.kpis.topCountry;
        
        // --- CHART 1: TEMPORAL ---
        const years = rslData.temporal.map(d => d.PY);
        const articles = rslData.temporal.map(d => d.Articulos);
        const avgCitations = rslData.temporal.map(d => Math.round(d.Promedio_Citas * 100) / 100);
        
        const trace1 = {{
            x: years,
            y: articles,
            name: 'Artículos Publicados',
            type: 'bar',
            marker: {{
                color: '#1e293b',
                opacity: 0.85
            }},
            offsetgroup: 1
        }};
        
        const trace2 = {{
            x: years,
            y: avgCitations,
            name: 'Promedio de Citas',
            type: 'scatter',
            yaxis: 'y2',
            mode: 'lines+markers',
            line: {{ color: '#f43f5e', width: 3 }},
            marker: {{ size: 8, color: '#f43f5e' }},
            offsetgroup: 2
        }};
        
        const layout1 = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '#f1f5f9', family: 'Inter, sans-serif' }},
            xaxis: {{
                gridcolor: '#222e45',
                tickmode: 'linear',
                tickformat: 'd'
            }},
            yaxis: {{
                title: 'Cantidad de Artículos',
                gridcolor: '#222e45',
                side: 'left'
            }},
            yaxis2: {{
                title: 'Promedio de Citas (Impacto)',
                gridcolor: 'rgba(0,0,0,0)',
                overlaying: 'y',
                side: 'right'
            }},
            legend: {{ orientation: 'h', y: -0.2, x: 0.5, xanchor: 'center' }},
            margin: {{ t: 20, b: 60, l: 50, r: 50 }},
            hovermode: 'closest'
        }};
        
        Plotly.newPlot('chart-temporal', [trace1, trace2], layout1, {{responsive: true, displayModeBar: false}});
        
        // --- CHART 2: BRADFORD'S LAW ---
        const bradData = rslData.bradford;
        const bradRanks = bradData.map(d => d.Rank);
        const bradCum = bradData.map(d => d.Cum_Count);
        const bradJournals = bradData.map(d => d.Journal);
        
        const traceBrad = {{
            x: bradRanks,
            y: bradCum,
            text: bradJournals.map((j, i) => `Rango ${{i+1}}: ${{j}}`),
            hoverinfo: 'text+y',
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#3b82f6', width: 2.5 }},
            marker: {{ size: 6, color: '#1e293b' }}
        }};
        
        const layoutBrad = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '#f1f5f9', family: 'Inter, sans-serif' }},
            xaxis: {{
                title: 'Rango de Revista (Escala Log)',
                type: 'log',
                gridcolor: '#222e45'
            }},
            yaxis: {{
                title: 'Artículos Acumulados',
                gridcolor: '#222e45'
            }},
            margin: {{ t: 20, b: 50, l: 50, r: 20 }},
            shapes: [
                {{
                    type: 'line',
                    x0: rslData.bradford_zone1_end,
                    y0: 0,
                    x1: rslData.bradford_zone1_end,
                    y1: rslData.kpis.totalArticles,
                    line: {{ color: '#f43f5e', width: 1.5, dash: 'dash' }}
                }},
                {{
                    type: 'line',
                    x0: rslData.bradford_zone2_end,
                    y0: 0,
                    x1: rslData.bradford_zone2_end,
                    y1: rslData.kpis.totalArticles,
                    line: {{ color: '#3b82f6', width: 1.5, dash: 'dash' }}
                }}
            ]
        }};
        
        Plotly.newPlot('chart-bradford', [traceBrad], layoutBrad, {{responsive: true, displayModeBar: false}});
        
        // --- CHART 3: COUNTRIES STACKED BAR ---
        const topCountries = rslData.countries.slice(0, 10).reverse();
        const countryNames = topCountries.map(d => d.Country);
        const scps = topCountries.map(d => d.SCP);
        const mcps = topCountries.map(d => d.MCP);
        
        const traceSCP = {{
            y: countryNames,
            x: scps,
            name: 'SCP (Coautoría Nacional)',
            type: 'bar',
            orientation: 'h',
            marker: {{
                color: '#0f766e',
                opacity: 0.85
            }}
        }};
        
        const traceMCP = {{
            y: countryNames,
            x: mcps,
            name: 'MCP (Coautoría Internacional)',
            type: 'bar',
            orientation: 'h',
            marker: {{
                color: '#f97316',
                opacity: 0.85
            }}
        }};
        
        const layoutCountry = {{
            barmode: 'stack',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '#f1f5f9', family: 'Inter, sans-serif' }},
            xaxis: {{
                title: 'Cantidad de Artículos',
                gridcolor: '#222e45'
            }},
            yaxis: {{
                gridcolor: '#222e45',
                tickmode: 'linear'
            }},
            legend: {{ orientation: 'h', y: -0.2, x: 0.5, xanchor: 'center' }},
            margin: {{ t: 20, b: 50, l: 120, r: 20 }}
        }};
        
        Plotly.newPlot('chart-countries', [traceSCP, traceMCP], layoutCountry, {{responsive: true, displayModeBar: false}});
        
        // --- CHART 4: TREEMAP ---
        const kwLabels = rslData.keywords.map(d => d.Keyword);
        const kwValues = rslData.keywords.map(d => d.Frecuencia);
        
        const traceTreemap = {{
            type: "treemap",
            labels: kwLabels,
            parents: kwLabels.map(() => ""),
            values: kwValues,
            textinfo: "label+value",
            textposition: "middle center",
            hoverinfo: "label+value",
            marker: {{
                colorscale: 'Mako',
                reversescale: true
            }}
        }};
        
        const layoutTreemap = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '#f1f5f9', family: 'Inter, sans-serif' }},
            margin: {{ t: 10, b: 10, l: 10, r: 10 }}
        }};
        
        Plotly.newPlot('chart-treemap', [traceTreemap], layoutTreemap, {{responsive: true, displayModeBar: false}});
        
        // --- CHART 5: THEMATIC MAP ---
        const themeData = rslData.thematic;
        const themeC = themeData.map(d => d.Centrality);
        const themeD = themeData.map(d => d.Density);
        const themeLabels = themeData.map(d => d.Keyword);
        const themeFreqs = themeData.map(d => d.Frequency);
        
        const traceTheme = {{
            x: themeC,
            y: themeD,
            text: themeLabels,
            mode: 'markers+text',
            textposition: 'top center',
            hoverinfo: 'text',
            hovertext: themeLabels.map((l, i) => `<b>${{l}}</b><br>Frecuencia: ${{themeFreqs[i]}}<br>Centralidad: ${{themeC[i]}}<br>Densidad: ${{themeD[i].toFixed(2)}}`),
            marker: {{
                size: themeFreqs.map(f => Math.max(12, f * 2.5)),
                color: '#f43f5e',
                opacity: 0.8,
                line: {{ color: '#ffffff', width: 1 }}
            }},
            type: 'scatter'
        }};
        
        const layoutTheme = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '#f1f5f9', family: 'Inter, sans-serif' }},
            xaxis: {{
                title: 'Centralidad (Relevancia / Conexión Externa)',
                gridcolor: '#222e45',
                zeroline: false
            }},
            yaxis: {{
                title: 'Densidad (Desarrollo / Cohesión Interna)',
                gridcolor: '#222e45',
                zeroline: false
            }},
            margin: {{ t: 20, b: 50, l: 50, r: 20 }},
            shapes: [
                {{
                    type: 'line',
                    x0: rslData.thematic_median_c,
                    y0: Math.min(...themeD) - 0.2,
                    x1: rslData.thematic_median_c,
                    y1: Math.max(...themeD) + 0.2,
                    line: {{ color: '#94a3b8', width: 1.5, dash: 'dash' }}
                }},
                {{
                    type: 'line',
                    x0: Math.min(...themeC) - 0.2,
                    y0: rslData.thematic_median_d,
                    x1: Math.max(...themeC) + 0.2,
                    y1: rslData.thematic_median_d,
                    line: {{ color: '#94a3b8', width: 1.5, dash: 'dash' }}
                }}
            ]
        }};
        
        Plotly.newPlot('chart-thematic', [traceTheme], layoutTheme, {{responsive: true, displayModeBar: false}});
        
        // --- CHART 6: SANKEY (THREE FIELDS PLOT) ---
        const sankeyData = rslData.sankey;
        const nodeColors = [];
        
        sankeyData.nodes.forEach((node, idx) => {{
            if (idx < sankeyData.country_count) {{
                nodeColors.push('#14b8a6');
            }} else if (idx < sankeyData.country_count + sankeyData.keyword_count) {{
                nodeColors.push('#8b5cf6');
            }} else {{
                nodeColors.push('#ec4899');
            }}
        }});
        
        const traceSankey = {{
            type: "sankey",
            orientation: "h",
            node: {{
                pad: 15,
                thickness: 20,
                line: {{ color: "rgba(0,0,0,0.3)", width: 0.5 }},
                label: sankeyData.nodes.map(n => n.name),
                color: nodeColors
            }},
            link: {{
                source: sankeyData.links.map(l => l.source),
                target: sankeyData.links.map(l => l.target),
                value: sankeyData.links.map(l => l.value),
                color: 'rgba(255, 255, 255, 0.12)'
            }}
        }};
        
        const layoutSankey = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '#f1f5f9', family: 'Inter, sans-serif' }},
            margin: {{ t: 20, b: 20, l: 10, r: 10 }}
        }};
        
        Plotly.newPlot('chart-sankey', [traceSankey], layoutSankey, {{responsive: true, displayModeBar: false}});

        // --- POPULATE TABLE ---
        const tableBody = document.getElementById('articles-table-body');
        
        function renderTable(data) {{
            tableBody.innerHTML = '';
            if (data.length === 0) {{
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No se encontraron artículos</td></tr>';
                return;
            }}
            
            data.forEach((art, index) => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="color: var(--text-muted); font-weight: 500;">${{index + 1}}</td>
                    <td>
                        <div class="article-title">${{escapeHtml(art.title)}}</div>
                    </td>
                    <td>
                        <div class="article-authors" title="${{escapeHtml(art.authors)}}">${{escapeHtml(art.authors)}}</div>
                    </td>
                    <td style="color: var(--text-muted); font-size: 0.85rem;">${{escapeHtml(art.journal)}}</td>
                    <td style="text-align: center;"><span class="badge badge-year">${{art.year}}</span></td>
                    <td style="text-align: center;"><span class="badge badge-citations">${{art.citations}}</span></td>
                `;
                tableBody.appendChild(row);
            }});
        }}
        
        function escapeHtml(str) {{
            return str
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }}
        
        renderTable(rslData.articles);
        
        // --- TABLE SEARCH FILTER ---
        const searchInput = document.getElementById('table-search');
        searchInput.addEventListener('input', function(e) {{
            const query = e.target.value.toLowerCase().trim();
            const filtered = rslData.articles.filter(art => {{
                return art.title.toLowerCase().includes(query) || 
                       art.authors.toLowerCase().includes(query) || 
                       art.journal.toLowerCase().includes(query) ||
                       art.keywords.toLowerCase().includes(query);
            }});
            renderTable(filtered);
        }});
    </script>
</body>
</html>
"""
    
    with open('rsl_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("Saved 'rsl_dashboard.html' successfully!")

if __name__ == '__main__':
    # Generar gráficos normales y el dashboard
    run_analysis(no_title=False)
    
    # Generar variantes sin título en una carpeta distinta
    run_analysis(no_title=True, output_dir='graficos_sin_titulo')
