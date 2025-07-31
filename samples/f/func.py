"""
サンプル関数: 数値を2倍にする関数
入力値を2倍して出力する簡単な関数

使用方法:
    python func.py -i <input_var> -o <output_code>
"""

import argparse
import json
import os


def double_value(input_value):
    """
    入力値を2倍にする関数
    
    Args:
        input_value: 入力値（数値または数値の文字列）
        
    Returns:
        入力値の2倍
    """
    try:
        # 数値に変換して2倍にする
        if isinstance(input_value, str):
            try:
                # 整数として解析を試行
                num = int(input_value)
            except ValueError:
                # 浮動小数点として解析を試行
                num = float(input_value)
        else:
            num = input_value
            
        result = num * 2
        return result
        
    except (ValueError, TypeError) as e:
        print(f"エラー: 数値に変換できません: {input_value}")
        raise e


def load_input_data(input_var_name):
    """
    入力変数のデータを読み込む
    
    Args:
        input_var_name (str): 入力変数名
        
    Returns:
        入力データ
    """
    # 現在のディレクトリで入力変数のフォルダを検索
    current_dir = os.getcwd()
    
    # 各フォルダをチェックして該当する変数を探す
    for folder_name in os.listdir(current_dir):
        folder_path = os.path.join(current_dir, folder_name)
        if os.path.isdir(folder_path):
            system_json_path = os.path.join(folder_path, "system.json")
            if os.path.exists(system_json_path):
                try:
                    with open(system_json_path, 'r', encoding='utf-8') as f:
                        system_data = json.load(f)
                    
                    # 変数名が一致するかチェック
                    if system_data.get("name") == input_var_name:
                        # data.csvを読み込む
                        data_csv_path = os.path.join(folder_path, "data.csv")
                        if os.path.exists(data_csv_path):
                            with open(data_csv_path, 'r', encoding='utf-8') as f:
                                content = f.read().strip()
                                return content
                        else:
                            print(f"警告: data.csvが見つかりません: {data_csv_path}")
                            return "10"  # デフォルト値
                            
                except Exception as e:
                    print(f"データ読み込みエラー: {e}")
                    continue
    
    print(f"警告: 入力変数 '{input_var_name}' が見つかりません。デフォルト値を使用します。")
    return "10"  # デフォルト値


def save_output_data(output_code, result):
    """
    出力データを保存
    
    Args:
        output_code (str): 出力フォルダのコード
        result: 計算結果
    """
    output_folder = os.path.join(os.getcwd(), output_code)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # data.csvに結果を保存
    data_csv_path = os.path.join(output_folder, "data.csv")
    with open(data_csv_path, 'w', encoding='utf-8') as f:
        f.write(str(result))
    
    print(f"結果を保存しました: {data_csv_path} = {result}")


def main():
    """
    メイン処理
    """
    parser = argparse.ArgumentParser(description="数値を2倍にする関数")
    parser.add_argument("-i", "--input", required=True, help="入力変数名")
    parser.add_argument("-o", "--output", required=True, help="出力フォルダのコード")
    
    args = parser.parse_args()
    
    try:
        # 入力データを読み込み
        input_data = load_input_data(args.input)
        print(f"入力データ: {input_data}")
        
        # 関数を実行
        result = double_value(input_data)
        print(f"計算結果: {input_data} * 2 = {result}")
        
        # 結果を保存
        save_output_data(args.output, result)
        
        print("✓ 関数実行が完了しました")
        
    except Exception as e:
        print(f"関数実行中にエラーが発生しました: {e}")
        exit(1)


if __name__ == "__main__":
    main()
