"""
FGDB初期化スクリプト (init.py)
FGDBシステムの初期化を行い、MGとOGのルートノードを作成する

使用方法:
    python init.py
"""

import os
import sys
from lib import FGDB


def main():
    """
    FGDBシステムの初期化を実行
    
    実行内容:
    1. FGDBインスタンスを作成
    2. MGとOGのルートノードを作成
    3. fgdb.pickleファイルに保存
    """
    print("=== FGDB初期化スクリプト ===")
    print("Functional Graph DataBaseシステムを初期化します")
    
    # 既存のfgdb.pickleファイルがある場合の警告
    if os.path.exists("fgdb.pickle"):
        response = input("既存のfgdb.pickleファイルが見つかりました。上書きしますか？ (y/N): ")
        if response.lower() != 'y':
            print("初期化をキャンセルしました")
            return
    
    try:
        # FGDBインスタンスを作成
        fgdb = FGDB()
        print("FGDBインスタンスを作成しました")
        
        # ルートノードを作成
        fgdb.create_root_nodes()
        
        # データを保存
        fgdb.save("fgdb.pickle")
        
        # 統計情報を表示
        stats = fgdb.get_statistics()
        print("\n=== 初期化完了 ===")
        print(f"Management Graph: {stats['management_graph']['nodes']} nodes, {stats['management_graph']['edges']} edges")
        print(f"Operation Graph: {stats['operation_graph']['nodes']} nodes, {stats['operation_graph']['edges']} edges")
        print(f"総ブロック数: {stats['total_blocks']}")
        print("\n初期化が正常に完了しました")
        print("次のステップ: python add_block.py -f <function_folder> または python add_block.py -d <data_folder>")
        
    except Exception as e:
        print(f"初期化中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
