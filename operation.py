"""
オペレーション実行スクリプト (operation.py)
operation.txtファイルから関数実行を解析し、バッチファイルを生成して実行する

使用方法:
    python operation.py -i operation.txt

機能:
1. operation.txtファイルを解析 (例: y=f(x))
2. バッチファイル(operation.bat)を自動生成
3. バッチファイルを実行して関数を呼び出し
4. 実行結果をFGDBに登録
"""

import os
import sys
import argparse
import subprocess
import re
from lib import FGDB


def parse_operation_file(operation_file):
    """
    operation.txtファイルを解析して関数実行情報を抽出
    
    サポートする形式:
    1. 名前形式: y=f(x)
    2. ハッシュコード形式: y=0f434271...(ebf7eb34...)
    
    Args:
        operation_file (str): operation.txtファイルのパス
        
    Returns:
        dict: 解析結果 {"output": "y", "function": "f", "input": "x", "use_codes": bool}
        None: 解析失敗時
    """
    try:
        with open(operation_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        print(f"operation.txtの内容: {content}")
        
        # パターン1: ハッシュコード形式 - y=hash1(hash2)
        hash_pattern = r'(\w+)\s*=\s*([a-f0-9]{64})\s*\(\s*([a-f0-9]{64})\s*\)'
        hash_match = re.match(hash_pattern, content)
        
        if hash_match:
            output_var = hash_match.group(1)
            function_code = hash_match.group(2)
            input_code = hash_match.group(3)
            
            result = {
                "output": output_var,
                "function": function_code,
                "input": input_code,
                "use_codes": True  # コードを使用するフラグ
            }
            
            print(f"ハッシュコード形式で解析: {result}")
            return result
        
        # パターン2: 名前形式 - y=f(x)
        name_pattern = r'(\w+)\s*=\s*(\w+)\s*\(\s*(\w+)\s*\)'
        name_match = re.match(name_pattern, content)
        
        if name_match:
            output_var = name_match.group(1)
            function_name = name_match.group(2)
            input_var = name_match.group(3)
            
            result = {
                "output": output_var,
                "function": function_name,
                "input": input_var,
                "use_codes": False  # 名前を使用するフラグ
            }
            
            print(f"名前形式で解析: {result}")
            return result
        
        # どちらのパターンにもマッチしない場合
        print(f"エラー: operation.txtの形式が正しくありません")
        print(f"サポートされる形式:")
        print(f"  1. 名前形式: y=f(x)")
        print(f"  2. コード形式: y=0f434271...(ebf7eb34...)")
        return None
            
    except Exception as e:
        print(f"operation.txtの読み込み中にエラーが発生しました: {e}")
        return None


def create_batch_file(operation_info, output_code, function_folder_code, input_var_name):
    """
    operation情報からバッチファイルを生成
    
    Args:
        operation_info (dict): 解析された実行情報
        output_code (str): 出力データブロックのハッシュコード
        function_folder_code (str): 関数フォルダの実際のハッシュコード
        input_var_name (str): 入力変数名（バッチ内で使用）
        
    Returns:
        str: 生成されたバッチファイルのパス
    """
    # バッチファイルの内容を作成
    # 例: python ./561f928a.../func.py -i x -o {output_code}
    batch_content = f"python ./{function_folder_code}/func.py -i {input_var_name} -o {output_code}"
    
    # バッチファイルを書き込み
    batch_file_path = "operation.bat"
    try:
        with open(batch_file_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"バッチファイルを生成しました: {batch_file_path}")
        print(f"バッチファイル内容: {batch_content}")
        return batch_file_path
        
    except Exception as e:
        print(f"バッチファイル生成中にエラーが発生しました: {e}")
        return None


def execute_batch_file(batch_file_path):
    """
    バッチファイルを実行
    
    Args:
        batch_file_path (str): 実行するバッチファイルのパス
        
    Returns:
        bool: 実行成功時True
    """
    try:
        print(f"バッチファイルを実行中: {batch_file_path}")
        
        # バッチファイルの内容を読み取ってコマンドとして直接実行
        with open(batch_file_path, 'r', encoding='utf-8') as f:
            command = f.read().strip()
        
        print(f"実行コマンド: {command}")
        
        # コマンドを直接実行
        result = subprocess.run(command, shell=True, 
                              capture_output=True, text=True, 
                              cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✓ バッチファイルの実行が完了しました")
            if result.stdout:
                print(f"出力: {result.stdout}")
            return True
        else:
            print(f"✗ バッチファイルの実行でエラーが発生しました (終了コード: {result.returncode})")
            if result.stderr:
                print(f"エラー出力: {result.stderr}")
            if result.stdout:
                print(f"標準出力: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"バッチファイル実行中にエラーが発生しました: {e}")
        return False


def main():
    """
    メイン処理
    operation.txtファイルを解析してバッチ実行し、結果をFGDBに登録
    """
    parser = argparse.ArgumentParser(
        description="operation.txtから関数実行を行いFGDBに結果を登録",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python operation.py -i operation.txt
  
operation.txtの形式:
  y=f(x)  # 出力変数=関数名(入力変数)
        """
    )
    
    parser.add_argument("-i", "--input", required=True, metavar="FILE",
                       help="実行するoperation.txtファイルのパス")
    
    args = parser.parse_args()
    
    # fgdb.pickleファイルの存在確認
    if not os.path.exists("fgdb.pickle"):
        print("エラー: fgdb.pickleファイルが見つかりません")
        print("先にinit.pyを実行してFGDBを初期化してください")
        sys.exit(1)
    
    # operation.txtファイルの存在確認
    if not os.path.exists(args.input):
        print(f"エラー: ファイル '{args.input}' が見つかりません")
        sys.exit(1)
    
    try:
        # FGDBをロード
        fgdb = FGDB()
        fgdb.load("fgdb.pickle")
        print("FGDBを読み込みました")
        
        # operation.txtを解析
        operation_info = parse_operation_file(args.input)
        if not operation_info:
            sys.exit(1)
        
        # 関数ブロックのコードを取得
        if operation_info["use_codes"]:
            # ハッシュコード形式の場合、直接コードを使用
            function_node = operation_info["function"]
            input_node = operation_info["input"]
            
            # コードが実際に存在するかチェック
            if function_node not in fgdb.blocks:
                print(f"関数コード '{function_node}' が見つかりません")
                sys.exit(1)
            
            if input_node not in fgdb.blocks:
                print(f"入力データコード '{input_node}' が見つかりません")
                sys.exit(1)
            
            # ブロック名を取得（バッチファイル内で使用するため）
            function_name = fgdb.blocks[function_node].get("name", "unknown")
            input_name = fgdb.blocks[input_node].get("name", "unknown")
            
            print(f"ハッシュコード使用: 関数 '{function_name}' ({function_node[:8]}), 入力 '{input_name}' ({input_node[:8]})")
        else:
            # 名前形式の場合、名前からコードを検索
            function_node = fgdb._find_node_by_name(operation_info["function"])
            if not function_node:
                print(f"関数 '{operation_info['function']}' が見つかりません")
                sys.exit(1)
            
            input_node = fgdb._find_node_by_name(operation_info["input"])
            if not input_node:
                print(f"入力変数 '{operation_info['input']}' が見つかりません")
                sys.exit(1)
            
            function_name = operation_info["function"]
            input_name = operation_info["input"]
            
            print(f"名前使用: 関数 '{function_name}', 入力 '{input_name}'")
        
        # 出力データブロックを事前に登録（バッチファイル生成のため）
        if operation_info["use_codes"]:
            # ハッシュコード形式の場合、名前で登録
            input_name = fgdb.blocks[input_node].get("name", "unknown")
            function_name = fgdb.blocks[function_node].get("name", "unknown")
            output_code = fgdb.register_operation_result(
                input_name, 
                function_name, 
                operation_info["output"]
            )
        else:
            # 名前形式の場合
            output_code = fgdb.register_operation_result(
                operation_info["input"], 
                operation_info["function"], 
                operation_info["output"]
            )
        
        if not output_code:
            print("出力データブロックの登録に失敗しました")
            sys.exit(1)
        
        # バッチファイルを生成
        if operation_info["use_codes"]:
            # ハッシュコード形式の場合、実際のコードを使用
            batch_file_path = create_batch_file(operation_info, output_code, function_node, input_node)
        else:
            # 名前形式の場合、実際のコードを使用（フォルダ名はコードであるため）
            batch_file_path = create_batch_file(operation_info, output_code, function_node, input_node)
        if not batch_file_path:
            sys.exit(1)
        
        # バッチファイルを実行
        if execute_batch_file(batch_file_path):
            print("✓ 関数実行が正常に完了しました")
            
            # system.jsonを出力フォルダに保存
            output_folder = os.path.join(os.getcwd(), output_code)
            system_json_path = os.path.join(output_folder, "system.json")
            
            if os.path.exists(system_json_path):
                print(f"✓ system.jsonが出力フォルダに保存されました: {system_json_path}")
            else:
                print(f"警告: system.jsonが見つかりません: {system_json_path}")
        else:
            print("✗ 関数実行に失敗しました")
            sys.exit(1)
        
        # FGDBを保存
        fgdb.save("fgdb.pickle")
        
        # 統計情報を表示
        stats = fgdb.get_statistics()
        print("\n=== 実行後のFGDB統計 ===")
        print(f"関数ブロック: {stats['function_blocks']}")
        print(f"データブロック: {stats['data_blocks']}")
        print(f"総ブロック数: {stats['total_blocks']}")
        print(f"Operation Graph: {stats['operation_graph']['nodes']} nodes, {stats['operation_graph']['edges']} edges")
        
        # バッチファイルを削除
        try:
            os.remove(batch_file_path)
            print(f"一時バッチファイルを削除しました: {batch_file_path}")
        except:
            pass
            
    except Exception as e:
        print(f"実行中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
