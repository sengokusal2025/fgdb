"""
ブロック追加スクリプト (add_block.py)
関数ブロック(FB)またはデータブロック(DB)をFGDBに登録する

使用方法:
    python add_block.py -f <function_block_folder>  # 関数ブロック追加
    python add_block.py -d <data_block_folder>      # データブロック追加

機能:
1. 指定されたフォルダをfgdbディレクトリにコピー
2. フォルダ名をハッシュ値に変更
3. system.jsonファイルを作成
4. FGDBに登録
"""

import os
import sys
import argparse
from lib import FGDB


def validate_folder_path(folder_path):
    """
    フォルダパスの妥当性を検証
    
    Args:
        folder_path (str): 検証するフォルダパス
        
    Returns:
        bool: パスが有効な場合True
    """
    if not os.path.exists(folder_path):
        print(f"エラー: フォルダ '{folder_path}' が見つかりません")
        return False
        
    if not os.path.isdir(folder_path):
        print(f"エラー: '{folder_path}' はフォルダではありません")
        return False
        
    return True


def add_function_block(fgdb, folder_path):
    """
    関数ブロックをFGDBに追加
    
    Args:
        fgdb (FGDB): FGDBインスタンス
        folder_path (str): 関数ブロックフォルダのパス
        
    Returns:
        str: 生成されたブロックコード、失敗時はNone
    """
    print(f"関数ブロックを追加中: {folder_path}")
    
    # フォルダ内にfunc.pyとfunc.txtがあるかチェック
    func_py_path = os.path.join(folder_path, "func.py")
    func_txt_path = os.path.join(folder_path, "func.txt")
    
    if not os.path.exists(func_py_path):
        print(f"警告: func.py が見つかりません: {func_py_path}")
    
    if not os.path.exists(func_txt_path):
        print(f"警告: func.txt が見つかりません: {func_txt_path}")
    
    try:
        code = fgdb.add_function_block(folder_path)
        return code
    except Exception as e:
        print(f"関数ブロックの追加中にエラーが発生しました: {e}")
        return None


def add_data_block(fgdb, folder_path):
    """
    データブロックをFGDBに追加
    
    Args:
        fgdb (FGDB): FGDBインスタンス
        folder_path (str): データブロックフォルダのパス
        
    Returns:
        str: 生成されたブロックコード、失敗時はNone
    """
    print(f"データブロックを追加中: {folder_path}")
    
    # フォルダ内にdata.csvがあるかチェック
    data_csv_path = os.path.join(folder_path, "data.csv")
    
    if not os.path.exists(data_csv_path):
        print(f"警告: data.csv が見つかりません: {data_csv_path}")
    
    try:
        code = fgdb.add_data_block(folder_path)
        return code
    except Exception as e:
        print(f"データブロックの追加中にエラーが発生しました: {e}")
        return None


def main():
    """
    メイン処理
    コマンドライン引数を解析してブロックを追加
    """
    parser = argparse.ArgumentParser(
        description="FGDBに関数ブロックまたはデータブロックを追加",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python add_block.py -f ./functions/add_func     # 関数ブロック追加
  python add_block.py -d ./data/input_data        # データブロック追加
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--function", metavar="FOLDER", 
                      help="追加する関数ブロックフォルダのパス")
    group.add_argument("-d", "--data", metavar="FOLDER", 
                      help="追加するデータブロックフォルダのパス")
    
    args = parser.parse_args()
    
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
        
        # 関数ブロックの場合
        if args.function:
            if not validate_folder_path(args.function):
                sys.exit(1)
            
            code = add_function_block(fgdb, args.function)
            if code:
                print(f"✓ 関数ブロックの追加が完了しました (コード: {code[:8]})")
            else:
                sys.exit(1)
        
        # データブロックの場合
        elif args.data:
            if not validate_folder_path(args.data):
                sys.exit(1)
            
            code = add_data_block(fgdb, args.data)
            if code:
                print(f"✓ データブロックの追加が完了しました (コード: {code[:8]})")
            else:
                sys.exit(1)
        
        # FGDBを保存
        fgdb.save("fgdb.pickle")
        
        # 統計情報を表示
        stats = fgdb.get_statistics()
        print("\n=== 現在のFGDB統計 ===")
        print(f"関数ブロック: {stats['function_blocks']}")
        print(f"データブロック: {stats['data_blocks']}")
        print(f"総ブロック数: {stats['total_blocks']}")
        print(f"Management Graph: {stats['management_graph']['nodes']} nodes, {stats['management_graph']['edges']} edges")
        print(f"Operation Graph: {stats['operation_graph']['nodes']} nodes, {stats['operation_graph']['edges']} edges")
        
    except Exception as e:
        print(f"実行中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
