"""
FGDB Interactive Visualization Script (show_fgdb.py)
Visualize FGDB's Management Graph (MG) and Operation Graph (OG) using pyvis

Usage:
    python show_fgdb.py

Features:
1. Load FGDB data from fgdb.pickle file
2. Interactive visualization using pyvis
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
import pyperclip
from pyvis.network import Network
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


def create_network_graph(graph, blocks, title="Graph"):
    """
    Create a pyvis Network from NetworkX graph
    
    Args:
        graph (nx.DiGraph): NetworkX directed graph
        blocks (dict): Block information dictionary
        title (str): Graph title
        
    Returns:
        Network: pyvis Network object
    """
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Configure physics
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": {"iterations": 100}
      },
      "interaction": {
        "dragNodes": true,
        "dragView": true,
        "zoomView": true
      }
    }
    """)
    
    # Add nodes
    for node in graph.nodes():
        node_data = blocks.get(node, {})
        shape, color = get_node_shape_and_color(node_data)
        
        # Node label (use head value or first 8 characters)
        label = node_data.get("head", node[:8])
        
        # Node title (tooltip)
        category = node_data.get("category", "unknown")
        name = node_data.get("name", "unknown")
        title_text = f"Category: {category}\\nName: {name}\\nCode: {node[:8]}...\\nClick to copy full code"
        
        net.add_node(
            node,
            label=label,
            shape=shape,
            color=color,
            title=title_text,
            size=25
        )
    
    # Add edges
    for source, target, edge_data in graph.edges(data=True):
        # Edge label (function name for Operation Graph)
        edge_label = edge_data.get('function', '')
        
        net.add_edge(
            source,
            target,
            label=edge_label,
            arrows="to",
            color="gray"
        )
    
    return net


def create_combined_html(mg_net, og_net, stats, blocks_info):
    """
    Create HTML file with both graphs and control buttons
    
    Args:
        mg_net (Network): Management Graph network
        og_net (Network): Operation Graph network
        stats (dict): Statistics information
        blocks_info (str): Blocks information text
    """
    # Generate HTML for individual networks
    mg_html = mg_net.generate_html()
    og_html = og_net.generate_html()
    
    # Extract the network div and script from each HTML
    import re
    
    # Extract MG network content
    mg_div_match = re.search(r'<div id="[^"]*"[^>]*></div>', mg_html)
    mg_script_match = re.search(r'<script type="text/javascript">(.*?)</script>', mg_html, re.DOTALL)
    
    mg_div = mg_div_match.group(0).replace('id="', 'id="mg_') if mg_div_match else ""
    mg_script = mg_script_match.group(1) if mg_script_match else ""
    mg_script = mg_script.replace('document.getElementById("', 'document.getElementById("mg_')
    
    # Extract OG network content
    og_div_match = re.search(r'<div id="[^"]*"[^>]*></div>', og_html)
    og_script_match = re.search(r'<script type="text/javascript">(.*?)</script>', og_html, re.DOTALL)
    
    og_div = og_div_match.group(0).replace('id="', 'id="og_') if og_div_match else ""
    og_script = og_script_match.group(1) if og_script_match else ""
    og_script = og_script.replace('document.getElementById("', 'document.getElementById("og_')
    
    # Create combined HTML
    combined_html = f"""
<!DOCTYPE html>
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
            {mg_div}
        </div>
        <div class="graph-box">
            <div class="graph-title">Operation Graph (OG)</div>
            {og_div}
        </div>
    </div>
    
    <div id="mg-single" class="single-view">
        <div class="graph-title">Management Graph (MG) - 単独表示</div>
        <div id="mg_single_network" style="height: 100%;"></div>
    </div>
    
    <div id="og-single" class="single-view">
        <div class="graph-title">Operation Graph (OG) - 単独表示</div>
        <div id="og_single_network" style="height: 100%;"></div>
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
        // Store network instances
        let mgNetwork, ogNetwork, mgSingleNetwork, ogSingleNetwork;
        
        // Initialize networks
        {mg_script}
        mgNetwork = network;
        
        {og_script}
        ogNetwork = network;
        
        // Add click handlers for copying node codes to clipboard
        function addClickHandler(network, blocks) {{
            network.on("click", function(params) {{
                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    try {{
                        // Copy full node code to clipboard
                        navigator.clipboard.writeText(nodeId).then(function() {{
                            // Show notification
                            showNotification('コードをクリップボードにコピーしました: ' + nodeId.substring(0, 16) + '...');
                        }}).catch(function(err) {{
                            console.error('Failed to copy to clipboard:', err);
                            // Fallback: show the code in alert
                            alert('コード: ' + nodeId);
                        }});
                    }} catch (err) {{
                        console.error('Clipboard access failed:', err);
                        alert('コード: ' + nodeId);
                    }}
                }}
            }});
        }}
        
        // Add click handlers
        addClickHandler(mgNetwork);
        addClickHandler(ogNetwork);
        
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
                // Recreate MG network for single view
                {mg_script.replace('document.getElementById("mg_', 'document.getElementById("mg_single_')}
                mgSingleNetwork = network;
                addClickHandler(mgSingleNetwork);
            }}
            
            updateActiveButton(1);
        }}
        
        function showOGOnly() {{
            document.getElementById('parallel-view').style.display = 'none';
            document.getElementById('mg-single').style.display = 'none';
            document.getElementById('og-single').style.display = 'block';
            
            // Create single OG network if not exists
            if (!ogSingleNetwork) {{
                // Recreate OG network for single view
                {og_script.replace('document.getElementById("og_', 'document.getElementById("og_single_')}
                ogSingleNetwork = network;
                addClickHandler(ogSingleNetwork);
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
                document.body.removeChild(notification);
            }}, 3000);
        }}
        
        // Initialize with parallel view
        showParallel();
    </script>
</body>
</html>"""
    
    # Write combined HTML to file
    with open("fgdb_visualization.html", "w", encoding="utf-8") as f:
        f.write(combined_html)


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
        
        # Create pyvis networks
        print("\\nCreating interactive visualization...")
        
        # Create Management Graph network
        mg_net = create_network_graph(
            fgdb.management_graph, 
            fgdb.blocks, 
            "Management Graph (MG)"
        )
        
        # Create Operation Graph network
        og_net = create_network_graph(
            fgdb.operation_graph, 
            fgdb.blocks, 
            "Operation Graph (OG)"
        )
        
        # Get statistics
        stats = fgdb.get_statistics()
        
        # Create combined HTML file
        create_combined_html(mg_net, og_net, stats, blocks_info)
        
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
        
    except ImportError as e:
        if "pyvis" in str(e):
            print("Error: pyvis library not found")
            print("Please install it with: pip install pyvis")
        elif "pyperclip" in str(e):
            print("Error: pyperclip library not found")
            print("Please install it with: pip install pyperclip")
        else:
            print(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during visualization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
