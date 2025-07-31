"""
FGDB Interactive Visualization Script (show_fgdb.py)
Visualize FGDB's Management Graph (MG) and Operation Graph (OG) using vis.js

Usage:
    python show_fgdb.py

Features:
1. Load FGDB data from fgdb.pickle file
2. Interactive visualization using vis.js (without pyvis)
3. Node shapes and colors:
   - Root: Diamond (gold)
   - Function Block: Rectangle (skyblue) 
   - Data Block: Ellipse (palegreen)
4. Draggable nodes
5. Click node to copy code to clipboard
6. Parallel display by default with toggle buttons for individual views
"""

import os
import sys
import webbrowser
import json
from lib import FGDB


def get_node_shape_and_color(node_data):
    """
    Determine node shape and color based on category
    
    Args:
        node_data (dict): Node data dictionary
        
    Returns:
        tuple: (shape, color) pair
    """
    category = node_data.get("category", "unknown")
    
    if category == "root":
        return "diamond", "#FFD700"  # Diamond, gold
    elif category == "function":
        return "box", "#87CEEB"  # Rectangle, skyblue
    elif category == "data":
        return "ellipse", "#98FB98"  # Ellipse, palegreen
    else:
        return "ellipse", "#CCCCCC"  # Default: ellipse, gray


def create_graph_data(graph, blocks):
    """
    Create vis.js compatible graph data
    
    Args:
        graph (nx.DiGraph): NetworkX directed graph
        blocks (dict): Block information dictionary
        
    Returns:
        tuple: (nodes_list, edges_list)
    """
    nodes_list = []
    edges_list = []
    
    print(f"Processing graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    
    # Create nodes data
    for node in graph.nodes():
        node_data = blocks.get(node, {})
        shape, color = get_node_shape_and_color(node_data)
        
        # Node label (use head value or first 8 characters)
        label = node_data.get("head", node[:8])
        
        # Node title (tooltip)
        category = node_data.get("category", "unknown")
        name = node_data.get("name", "unknown")
        title_text = f"Category: {category}\\nName: {name}\\nCode: {node[:8]}...\\nClick to copy full code"
        
        print(f"Adding node: {label} ({category})")
        
        node_obj = {
            "id": node,
            "label": label,
            "shape": shape,
            "color": color,
            "title": title_text,
            "size": 25,
            "font": {"size": 14, "color": "black"}
        }
        
        nodes_list.append(node_obj)
    
    # Create edges data
    for source, target, edge_data in graph.edges(data=True):
        edge_label = edge_data.get('function', '')
        
        source_label = blocks.get(source, {}).get('head', source[:8])
        target_label = blocks.get(target, {}).get('head', target[:8])
        print(f"Adding edge: {source_label} -> {target_label}")
        
        edge_obj = {
            "from": source,
            "to": target,
            "label": edge_label,
            "arrows": "to",
            "color": "gray",
            "width": 2
        }
        
        edges_list.append(edge_obj)
    
    return nodes_list, edges_list


def create_html_file(mg_nodes, mg_edges, og_nodes, og_edges, stats, blocks_info):
    """
    Create HTML file with interactive visualization
    
    Args:
        mg_nodes (list): Management Graph nodes data
        mg_edges (list): Management Graph edges data
        og_nodes (list): Operation Graph nodes data
        og_edges (list): Operation Graph edges data
        stats (dict): Statistics information
        blocks_info (str): Blocks information text
    """
    
    # Convert data to JSON strings
    mg_nodes_json = json.dumps(mg_nodes, indent=2)
    mg_edges_json = json.dumps(mg_edges, indent=2)
    og_nodes_json = json.dumps(og_nodes, indent=2)
    og_edges_json = json.dumps(og_edges, indent=2)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>FGDB Interactive Visualization</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .controls {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .btn {{
            padding: 10px 20px;
            margin: 0 5px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        .btn:hover {{
            background-color: #45a049;
        }}
        .btn.active {{
            background-color: #2196F3;
        }}
        .graph-container {{
            display: flex;
            gap: 20px;
            height: 600px;
        }}
        .graph-box {{
            flex: 1;
            border: 2px solid #ddd;
            border-radius: 8px;
            background-color: white;
            position: relative;
        }}
        .graph-title {{
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(255,255,255,0.8);
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
            z-index: 1000;
        }}
        .single-view {{
            display: none;
            height: 600px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background-color: white;
            position: relative;
        }}
        .info-panel {{
            margin-top: 20px;
            padding: 15px;
            background-color: white;
            border-radius: 8px;
            border: 1px solid #ddd;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        .stat-item {{
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
            text-align: center;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 15px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-shape {{
            width: 20px;
            height: 20px;
        }}
        .diamond {{
            background-color: #FFD700;
            transform: rotate(45deg);
        }}
        .rectangle {{
            background-color: #87CEEB;
        }}
        .ellipse {{
            background-color: #98FB98;
            border-radius: 50%;
        }}
        #mg-network, #og-network, #mg-single-network, #og-single-network {{
            width: 100%;
            height: 100%;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔗 FGDB Interactive Visualization</h1>
        <p>Functional Graph DataBase - インタラクティブグラフ可視化</p>
    </div>
    
    <div class="controls">
        <button class="btn active" onclick="showParallel()">並列表示 (Both Graphs)</button>
        <button class="btn" onclick="showMGOnly()">MG単独表示 (Management Graph Only)</button>
        <button class="btn" onclick="showOGOnly()">OG単独表示 (Operation Graph Only)</button>
    </div>
    
    <div id="parallel-view" class="graph-container">
        <div class="graph-box">
            <div class="graph-title">Management Graph (MG)</div>
            <div id="mg-network"></div>
        </div>
        <div class="graph-box">
            <div class="graph-title">Operation Graph (OG)</div>
            <div id="og-network"></div>
        </div>
    </div>
    
    <div id="mg-single" class="single-view">
        <div class="graph-title">Management Graph (MG) - 単独表示</div>
        <div id="mg-single-network"></div>
    </div>
    
    <div id="og-single" class="single-view">
        <div class="graph-title">Operation Graph (OG) - 単独表示</div>
        <div id="og-single-network"></div>
    </div>
    
    <div class="info-panel">
        <div class="legend">
            <div class="legend-item">
                <div class="legend-shape diamond"></div>
                <span>Root (ルート)</span>
            </div>
            <div class="legend-item">
                <div class="legend-shape rectangle"></div>
                <span>Function Block (関数ブロック)</span>
            </div>
            <div class="legend-item">
                <div class="legend-shape ellipse"></div>
                <span>Data Block (データブロック)</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <strong>Management Graph</strong><br>
                ノード: {stats['management_graph']['nodes']}<br>
                エッジ: {stats['management_graph']['edges']}
            </div>
            <div class="stat-item">
                <strong>Operation Graph</strong><br>
                ノード: {stats['operation_graph']['nodes']}<br>
                エッジ: {stats['operation_graph']['edges']}
            </div>
            <div class="stat-item">
                <strong>関数ブロック</strong><br>
                {stats['function_blocks']} 個
            </div>
            <div class="stat-item">
                <strong>データブロック</strong><br>
                {stats['data_blocks']} 個
            </div>
        </div>
        
        <details>
            <summary><strong>📋 ブロック一覧 (クリックで展開)</strong></summary>
            <pre style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; overflow-x: auto;">{blocks_info}</pre>
        </details>
        
        <div style="margin-top: 15px; padding: 10px; background-color: #e3f2fd; border-radius: 4px;">
            <strong>💡 使用方法:</strong><br>
            • ノードをドラッグして移動できます<br>
            • ノードをクリックすると、そのコードがクリップボードにコピーされます<br>
            • マウスホイールでズーム、ドラッグで画面移動ができます
        </div>
    </div>
    
    <script type="text/javascript">
        // Graph data
        const mgNodes = new vis.DataSet({mg_nodes_json});
        const mgEdges = new vis.DataSet({mg_edges_json});
        const ogNodes = new vis.DataSet({og_nodes_json});
        const ogEdges = new vis.DataSet({og_edges_json});
        
        // Network options
        const options = {{
            physics: {{
                enabled: true,
                stabilization: {{iterations: 100}},
                barnesHut: {{
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 95,
                    springConstant: 0.04,
                    damping: 0.09
                }}
            }},
            interaction: {{
                dragNodes: true,
                dragView: true,
                zoomView: true
            }},
            nodes: {{
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                shadow: true,
                smooth: {{
                    type: 'continuous'
                }}
            }}
        }};
        
        // Store network instances
        let mgNetwork, ogNetwork, mgSingleNetwork, ogSingleNetwork;
        
        // Initialize networks
        function initNetworks() {{
            console.log('Initializing networks...');
            console.log('MG Nodes:', mgNodes.get());
            console.log('MG Edges:', mgEdges.get());
            console.log('OG Nodes:', ogNodes.get());
            console.log('OG Edges:', ogEdges.get());
            
            // Management Graph (parallel view)
            mgNetwork = new vis.Network(
                document.getElementById('mg-network'),
                {{nodes: mgNodes, edges: mgEdges}},
                options
            );
            
            // Operation Graph (parallel view)
            ogNetwork = new vis.Network(
                document.getElementById('og-network'),
                {{nodes: ogNodes, edges: ogEdges}},
                options
            );
            
            // Add click handlers
            addClickHandler(mgNetwork, 'MG');
            addClickHandler(ogNetwork, 'OG');
            
            console.log('Networks initialized successfully');
        }}
        
        // Add click handlers for copying node codes to clipboard
        function addClickHandler(network, graphType) {{
            network.on("click", function(params) {{
                console.log('Click event:', params);
                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    console.log('Node clicked:', nodeId);
                    try {{
                        // Copy full node code to clipboard
                        if (navigator.clipboard && navigator.clipboard.writeText) {{
                            navigator.clipboard.writeText(nodeId).then(function() {{
                                showNotification('コードをクリップボードにコピーしました: ' + nodeId.substring(0, 16) + '...');
                            }}).catch(function(err) {{
                                console.error('Failed to copy to clipboard:', err);
                                fallbackCopy(nodeId);
                            }});
                        }} else {{
                            fallbackCopy(nodeId);
                        }}
                    }} catch (err) {{
                        console.error('Clipboard access failed:', err);
                        fallbackCopy(nodeId);
                    }}
                }}
            }});
        }}
        
        // Fallback copy method
        function fallbackCopy(text) {{
            // Try to use the older execCommand method
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {{
                const successful = document.execCommand('copy');
                if (successful) {{
                    showNotification('コードをクリップボードにコピーしました: ' + text.substring(0, 16) + '...');
                }} else {{
                    alert('コード: ' + text);
                }}
            }} catch (err) {{
                console.error('execCommand failed:', err);
                alert('コード: ' + text);
            }}
            document.body.removeChild(textArea);
        }}
        
        // View switching functions
        function showParallel() {{
            document.getElementById('parallel-view').style.display = 'flex';
            document.getElementById('mg-single').style.display = 'none';
            document.getElementById('og-single').style.display = 'none';
            updateActiveButton(0);
        }}
        
        function showMGOnly() {{
            document.getElementById('parallel-view').style.display = 'none';
            document.getElementById('mg-single').style.display = 'block';
            document.getElementById('og-single').style.display = 'none';
            
            // Create single MG network if not exists
            if (!mgSingleNetwork) {{
                mgSingleNetwork = new vis.Network(
                    document.getElementById('mg-single-network'),
                    {{nodes: mgNodes, edges: mgEdges}},
                    options
                );
                addClickHandler(mgSingleNetwork, 'MG-Single');
            }}
            
            updateActiveButton(1);
        }}
        
        function showOGOnly() {{
            document.getElementById('parallel-view').style.display = 'none';
            document.getElementById('mg-single').style.display = 'none';
            document.getElementById('og-single').style.display = 'block';
            
            // Create single OG network if not exists
            if (!ogSingleNetwork) {{
                ogSingleNetwork = new vis.Network(
                    document.getElementById('og-single-network'),
                    {{nodes: ogNodes, edges: ogEdges}},
                    options
                );
                addClickHandler(ogSingleNetwork, 'OG-Single');
            }}
            
            updateActiveButton(2);
        }}
        
        function updateActiveButton(activeIndex) {{
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach((btn, index) => {{
                if (index === activeIndex) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});
        }}
        
        // Notification function
        function showNotification(message) {{
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: #4CAF50;
                color: white;
                padding: 15px 20px;
                border-radius: 4px;
                z-index: 10000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                font-size: 14px;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {{
                if (document.body.contains(notification)) {{
                    document.body.removeChild(notification);
                }}
            }}, 3000);
        }}
        
        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded, initializing...');
            initNetworks();
            showParallel();
        }});
        
        // Also try to initialize after window load as fallback
        window.addEventListener('load', function() {{
            console.log('Window loaded');
            if (!mgNetwork || !ogNetwork) {{
                console.log('Networks not initialized, retrying...');
                setTimeout(initNetworks, 100);
            }}
        }});
    </script>
</body>
</html>"""
    
    return html_content


def print_graph_info(fgdb):
    """
    Print graph information to console
    
    Args:
        fgdb (FGDB): FGDB instance
        
    Returns:
        str: Formatted blocks information for HTML
    """
    stats = fgdb.get_statistics()
    
    print("=== FGDB Statistics ===")
    print(f"Management Graph: {stats['management_graph']['nodes']} nodes, {stats['management_graph']['edges']} edges")
    print(f"Operation Graph: {stats['operation_graph']['nodes']} nodes, {stats['operation_graph']['edges']} edges")
    print(f"Function Blocks: {stats['function_blocks']}")
    print(f"Data Blocks: {stats['data_blocks']}")
    print(f"Total Blocks: {stats['total_blocks']}")
    
    print("\\n=== Block List ===")
    blocks_info = ""
    for code, block_info in fgdb.blocks.items():
        category = block_info.get("category", "unknown")
        name = block_info.get("name", "unknown")
        head = block_info.get("head", code[:8])
        info_line = f"[{category.upper()}] {name} (Code: {head})"
        print(info_line)
        blocks_info += info_line + "\\n"
    
    return blocks_info


def main():
    """
    Main processing
    Load FGDB and create interactive visualization
    """
    # Check if fgdb.pickle file exists
    if not os.path.exists("fgdb.pickle"):
        print("Error: fgdb.pickle file not found")
        print("Please run init.py first to initialize FGDB")
        sys.exit(1)
    
    try:
        # Load FGDB
        fgdb = FGDB()
        fgdb.load("fgdb.pickle")
        print("FGDB loaded successfully")
        
        # Print graph information and get blocks info for HTML
        blocks_info = print_graph_info(fgdb)
        
        # Create vis.js compatible data
        print("\\nCreating interactive visualization...")
        
        mg_nodes, mg_edges = create_graph_data(fgdb.management_graph, fgdb.blocks)
        og_nodes, og_edges = create_graph_data(fgdb.operation_graph, fgdb.blocks)
        
        # Get statistics
        stats = fgdb.get_statistics()
        
        # Create HTML file
        html_content = create_html_file(mg_nodes, mg_edges, og_nodes, og_edges, stats, blocks_info)
        
        # Write HTML file
        with open("fgdb_visualization.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("✓ Interactive visualization created: fgdb_visualization.html")
        print("\\n🌐 Opening visualization in web browser...")
        
        # Open in web browser
        html_path = os.path.abspath("fgdb_visualization.html")
        webbrowser.open(f"file://{html_path}")
        
        print("\\n💡 Usage Instructions:")
        print("• Drag nodes to move them around")
        print("• Click nodes to copy their codes to clipboard")
        print("• Use mouse wheel to zoom, drag to pan")
        print("• Use buttons to switch between parallel and single views")
        
    except Exception as e:
        print(f"Error during visualization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
