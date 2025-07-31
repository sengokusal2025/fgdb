"""
FGDB可視化スクリプト (show_fgdb.py)
FGDBのManagement Graph (MG) と Operation Graph (OG) を可視化する

使用方法:
    python show_fgdb.py

機能:
1. fgdb.pickleファイルからFGDBデータを読み込み
2. MatplotlibでMGとOGを個別に表示
3. ノード形状とラベルを適切に設定
   - Root: ひし形 (diamond)
   - Function Block: 矩形 (rectangle) 
   - Data Block: 楕円 (ellipse)
"""

import os
import sys
import matplotlib.pyplot as plt
import networkx as nx
from lib import FGDB


def setup_matplotlib():
    """
    Matplotlibの設定
    日本語フォントと表示設定
    """
    plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
    plt.rcParams['figure.figsize'] = (15, 10)


def get_node_shape_and_color(node_data):
    """
    ノードの形状と色を決定
    
    Args:
        node_data (dict): ノードのデータ辞書
        
    Returns:
        tuple: (shape, color) の組
    """
    category = node_data.get("category", "unknown")
    
    if category == "root":
        return "D", "#FFD700"  # ひし形、金色
    elif category == "function":
        return "s", "#87CEEB"  # 矩形、スカイブルー
    elif category == "data":
        return "o", "#98FB98"  # 楕円、ペールグリーン
    else:
        return "o", "#CCCCCC"  # デフォルト：楕円、グレー


def draw_graph(graph, title, ax, blocks):
    """
    グラフを描画
    
    Args:
        graph (nx.DiGraph): 描画するグラフ
        title (str): グラフのタイトル
        ax (matplotlib.axes.Axes): 描画対象のAxes
        blocks (dict): ブロック情報辞書
    """
    if graph.number_of_nodes() == 0:
        ax.text(0.5, 0.5, f"{title}\n(ノードなし)", 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        return
    
    # レイアウトを計算（階層レイアウト）
    try:
        # 階層レイアウトを試行
        pos = nx.spring_layout(graph, k=3, iterations=50)
    except:
        # フォールバック: スプリングレイアウト
        pos = nx.spring_layout(graph)
    
    # ノードを形状と色別にグループ化
    node_groups = {}
    for node in graph.nodes():
        node_data = blocks.get(node, {})
        shape, color = get_node_shape_and_color(node_data)
        key = (shape, color)
        if key not in node_groups:
            node_groups[key] = []
        node_groups[key].append(node)
    
    # グループごとにノードを描画
    for (shape, color), nodes in node_groups.items():
        node_positions = {node: pos[node] for node in nodes}
        nx.draw_networkx_nodes(graph, node_positions, 
                             nodelist=nodes,
                             node_shape=shape,
                             node_color=color,
                             node_size=800,
                             alpha=0.8,
                             ax=ax)
    
    # エッジを描画
    nx.draw_networkx_edges(graph, pos, 
                          edge_color='gray',
                          arrows=True,
                          arrowsize=20,
                          arrowstyle='->',
                          alpha=0.6,
                          ax=ax)
    
    # ラベルを描画（head値を使用）
    labels = {}
    for node in graph.nodes():
        node_data = blocks.get(node, {})
        labels[node] = node_data.get("head", node[:8])
    
    nx.draw_networkx_labels(graph, pos, labels, 
                           font_size=8,
                           font_weight='bold',
                           ax=ax)
    
    # エッジラベルを描画（Operation Graphの場合）
    if "Operation" in title:
        edge_labels = {}
        for edge in graph.edges(data=True):
            source, target, data = edge
            func_name = data.get('function', '')
            if func_name:
                edge_labels[(source, target)] = func_name
        
        if edge_labels:
            nx.draw_networkx_edge_labels(graph, pos, edge_labels,
                                       font_size=6,
                                       ax=ax)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')


def create_legend(ax):
    """
    凡例を作成
    
    Args:
        ax (matplotlib.axes.Axes): 凡例を描画するAxes
    """
    legend_elements = [
        plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='#FFD700', 
                  markersize=10, label='Root (ルート)'),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#87CEEB', 
                  markersize=10, label='Function Block (関数ブロック)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#98FB98', 
                  markersize=10, label='Data Block (データブロック)')
    ]
    
    ax.legend(handles=legend_elements, loc='center', fontsize=12)
    ax.axis('off')


def print_graph_info(fgdb):
    """
    グラフ情報をコンソールに出力
    
    Args:
        fgdb (FGDB): FGDBインスタンス
    """
    stats = fgdb.get_statistics()
    
    print("=== FGDB 統計情報 ===")
    print(f"Management Graph: {stats['management_graph']['nodes']} nodes, {stats['management_graph']['edges']} edges")
    print(f"Operation Graph: {stats['operation_graph']['nodes']} nodes, {stats['operation_graph']['edges']} edges")
    print(f"関数ブロック: {stats['function_blocks']}")
    print(f"データブロック: {stats['data_blocks']}")
    print(f"総ブロック数: {stats['total_blocks']}")
    
    print("\n=== ブロック一覧 ===")
    for code, block_info in fgdb.blocks.items():
        category = block_info.get("category", "unknown")
        name = block_info.get("name", "unknown")
        head = block_info.get("head", code[:8])
        print(f"[{category.upper()}] {name} (コード: {head})")


def main():
    """
    メイン処理
    FGDBを読み込んでグラフを可視化
    """
    setup_matplotlib()
    
    # fgdb.pickleファイルの存在確認
    if not os.path.exists("fgdb.pickle"):
        print("エラー: fgdb.pickleファイルが見つかりません")
        print("先にinit.pyを実行してFGDBを初期化してください")
        sys.exit(1)
    
    try:
        # FGDBをロード
        fgdb = FGDB()
        fgdb.load("fgdb.pickle")
        print("FGDBを読み込みました")
        
        # グラフ情報を出力
        print_graph_info(fgdb)
        
        # 図を作成
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Management Graphを描画
        draw_graph(fgdb.management_graph, "Management Graph (MG)", ax1, fgdb.blocks)
        
        # Operation Graphを描画
        draw_graph(fgdb.operation_graph, "Operation Graph (OG)", ax2, fgdb.blocks)
        
        # 凡例を作成
        create_legend(ax3)
        
        # 統計情報をテキストで表示
        stats = fgdb.get_statistics()
        stats_text = f"""FGDB統計情報

Management Graph:
  ノード数: {stats['management_graph']['nodes']}
  エッジ数: {stats['management_graph']['edges']}

Operation Graph:
  ノード数: {stats['operation_graph']['nodes']}
  エッジ数: {stats['operation_graph']['edges']}

ブロック統計:
  関数ブロック: {stats['function_blocks']}
  データブロック: {stats['data_blocks']}
  総ブロック数: {stats['total_blocks']}
"""
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, 
                fontsize=11, verticalalignment='top', fontfamily='monospace')
        ax4.set_title("統計情報", fontsize=14, fontweight='bold')
        ax4.axis('off')
        
        # 全体タイトル
        fig.suptitle("Functional Graph DataBase (FGDB) 可視化", 
                    fontsize=16, fontweight='bold')
        
        # レイアウト調整
        plt.tight_layout()
        
        # 表示
        print("\nグラフウィンドウを表示しています...")
        print("ウィンドウを閉じるにはxボタンをクリックしてください")
        plt.show()
        
    except Exception as e:
        print(f"可視化中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
