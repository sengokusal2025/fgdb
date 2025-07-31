"""
FGDB (Functional Graph DataBase) Core Library
関数実行履歴を管理するためのコアライブラリ

このライブラリは以下の機能を提供します：
- Management Graph (MG): 構成要素の管理
- Operation Graph (OG): 実行履歴の管理
- ブロック管理機能
- グラフ操作機能
"""

import networkx as nx
import pickle
import json
import os
import hashlib
import time
import shutil
from datetime import datetime


class FGDB:
    """
    Functional Graph DataBase クラス
    
    MGとOGの2つのグラフを管理し、関数ブロック(FB)とデータブロック(DB)の
    登録・実行履歴の記録を行う
    """
    
    def __init__(self):
        """
        FGDBインスタンスの初期化
        Management Graph (MG) と Operation Graph (OG) を作成
        """
        self.management_graph = nx.DiGraph()  # Management Graph (MG)
        self.operation_graph = nx.DiGraph()   # Operation Graph (OG)
        self.blocks = {}  # ブロック情報を格納する辞書
        self.last_registered_node = None  # MGで最後に登録されたノード
        
    def create_root_nodes(self):
        """
        MGとOGにルートノードを作成
        ルートノードは特別な形状（ひし形）で表示される
        """
        # MGルートノード
        mg_root_info = {
            "category": "root",
            "name": "MG_ROOT",
            "id": "mg_root_" + str(int(time.time())),
            "shape": "diamond"
        }
        mg_root_code = self._generate_code(mg_root_info["id"])
        mg_root_info["code"] = mg_root_code
        mg_root_info["head"] = mg_root_code[:8]
        
        self.management_graph.add_node(mg_root_code, **mg_root_info)
        self.blocks[mg_root_code] = mg_root_info
        self.last_registered_node = mg_root_code
        
        # OGルートノード
        og_root_info = {
            "category": "root",
            "name": "OG_ROOT", 
            "id": "og_root_" + str(int(time.time())),
            "shape": "diamond"
        }
        og_root_code = self._generate_code(og_root_info["id"])
        og_root_info["code"] = og_root_code
        og_root_info["head"] = og_root_code[:8]
        
        self.operation_graph.add_node(og_root_code, **og_root_info)
        self.blocks[og_root_code] = og_root_info
        
        print("ルートノードを作成しました")
        print(f"MG Root: {mg_root_info['head']}")
        print(f"OG Root: {og_root_info['head']}")
        
    def _generate_code(self, id_value):
        """
        IDからハッシュコードを生成
        
        Args:
            id_value (str): ハッシュ化するID文字列
            
        Returns:
            str: SHA256ハッシュの16進数表現
        """
        return hashlib.sha256(id_value.encode()).hexdigest()
        
    def _generate_timestamp(self):
        """
        現在時刻のタイムスタンプを生成
        
        Returns:
            str: タイムスタンプ文字列
        """
        return str(int(time.time()))
        
    def add_function_block(self, block_folder_path):
        """
        関数ブロック(FB)をFGDBに登録
        
        Args:
            block_folder_path (str): 登録する関数ブロックフォルダのパス
            
        Returns:
            str: 生成されたブロックのコード
        """
        folder_name = os.path.basename(block_folder_path)
        timestamp = self._generate_timestamp()
        
        # ブロック情報を作成
        block_info = {
            "category": "function",
            "name": folder_name,
            "id": folder_name + timestamp,
            "shape": "rectangle"  # MGでの表示形状
        }
        
        code = self._generate_code(block_info["id"])
        block_info["code"] = code
        block_info["head"] = code[:8]
        
        # 新しいフォルダパスを作成
        new_folder_path = os.path.join(os.getcwd(), code)
        block_info["path"] = new_folder_path
        
        # フォルダをコピー
        if os.path.exists(block_folder_path):
            shutil.copytree(block_folder_path, new_folder_path)
            
            # system.jsonを作成
            system_json_path = os.path.join(new_folder_path, "system.json")
            with open(system_json_path, 'w', encoding='utf-8') as f:
                json.dump(block_info, f, indent=2, ensure_ascii=False)
                
        # MGに登録
        self.management_graph.add_node(code, **block_info)
        
        # 親ノードとの接続（登録順）
        if self.last_registered_node:
            self.management_graph.add_edge(self.last_registered_node, code)
            
        self.blocks[code] = block_info
        self.last_registered_node = code
        
        print(f"関数ブロック '{folder_name}' を登録しました (コード: {block_info['head']})")
        return code
        
    def add_data_block(self, block_folder_path):
        """
        データブロック(DB)をFGDBに登録
        
        Args:
            block_folder_path (str): 登録するデータブロックフォルダのパス
            
        Returns:
            str: 生成されたブロックのコード
        """
        folder_name = os.path.basename(block_folder_path)
        timestamp = self._generate_timestamp()
        
        # ブロック情報を作成
        block_info = {
            "category": "data",
            "name": folder_name,
            "id": folder_name + timestamp,
            "shape": "ellipse"  # 表示形状
        }
        
        code = self._generate_code(block_info["id"])
        block_info["code"] = code
        block_info["head"] = code[:8]
        
        # 新しいフォルダパスを作成
        new_folder_path = os.path.join(os.getcwd(), code)
        block_info["path"] = new_folder_path
        
        # フォルダをコピー
        if os.path.exists(block_folder_path):
            shutil.copytree(block_folder_path, new_folder_path)
            
            # system.jsonを作成
            system_json_path = os.path.join(new_folder_path, "system.json")
            with open(system_json_path, 'w', encoding='utf-8') as f:
                json.dump(block_info, f, indent=2, ensure_ascii=False)
                
        # MGに登録
        self.management_graph.add_node(code, **block_info)
        
        # 親ノードとの接続（登録順）
        if self.last_registered_node:
            self.management_graph.add_edge(self.last_registered_node, code)
            
        # OGにも登録（独立変数として）
        og_root = self._get_og_root()
        if og_root:
            self.operation_graph.add_node(code, **block_info)
            self.operation_graph.add_edge(og_root, code)
            
        self.blocks[code] = block_info
        self.last_registered_node = code
        
        print(f"データブロック '{folder_name}' を登録しました (コード: {block_info['head']})")
        return code
        
    def _get_og_root(self):
        """
        OGのルートノードを取得
        
        Returns:
            str: OGルートノードのコード、見つからない場合はNone
        """
        for node, data in self.operation_graph.nodes(data=True):
            if data.get("category") == "root" and data.get("name") == "OG_ROOT":
                return node
        return None
        
    def register_operation_result(self, input_var_name, function_name, output_var_name):
        """
        関数実行結果をOGに登録
        
        Args:
            input_var_name (str): 入力変数名
            function_name (str): 関数名
            output_var_name (str): 出力変数名
            
        Returns:
            str: 生成された出力データブロックのコード
        """
        # 入力変数ノードを検索
        input_node = self._find_node_by_name(input_var_name)
        if not input_node:
            print(f"入力変数 '{input_var_name}' が見つかりません")
            return None
            
        # 関数ブロックを検索
        function_node = self._find_node_by_name(function_name)
        if not function_node:
            print(f"関数 '{function_name}' が見つかりません")
            return None
            
        # 出力データブロックを作成
        timestamp = self._generate_timestamp()
        output_info = {
            "category": "data",
            "name": output_var_name,
            "id": output_var_name + timestamp,
            "shape": "ellipse"
        }
        
        output_code = self._generate_code(output_info["id"])
        output_info["code"] = output_code
        output_info["head"] = output_code[:8]
        
        # 出力フォルダを作成
        output_folder_path = os.path.join(os.getcwd(), output_code)
        os.makedirs(output_folder_path, exist_ok=True)
        output_info["path"] = output_folder_path
        
        # system.jsonを作成
        system_json_path = os.path.join(output_folder_path, "system.json")
        with open(system_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_info, f, indent=2, ensure_ascii=False)
            
        # OGに出力ノードを追加
        self.operation_graph.add_node(output_code, **output_info)
        
        # エッジを追加（入力→出力、関数名をエッジのラベルとして）
        self.operation_graph.add_edge(input_node, output_code, function=function_name)
        
        # MGにも出力データブロックを追加（登録順で接続）
        self.management_graph.add_node(output_code, **output_info)
        
        # MGで親ノードとの接続（登録順）
        if self.last_registered_node:
            self.management_graph.add_edge(self.last_registered_node, output_code)
        
        # 最後に登録されたノードを更新
        self.last_registered_node = output_code
        
        self.blocks[output_code] = output_info
        
        print(f"実行結果を登録しました: {input_var_name} -[{function_name}]-> {output_var_name} (コード: {output_info['head']})")
        return output_code
        
    def _find_node_by_name(self, name):
        """
        名前でノードを検索
        
        Args:
            name (str): 検索するノード名
            
        Returns:
            str: ノードのコード、見つからない場合はNone
        """
        for node, data in self.blocks.items():
            if data.get("name") == name:
                return node
        return None
        
    def save(self, filename="fgdb.pickle"):
        """
        FGDBデータをファイルに保存
        
        Args:
            filename (str): 保存ファイル名
        """
        data = {
            "management_graph": self.management_graph,
            "operation_graph": self.operation_graph,
            "blocks": self.blocks,
            "last_registered_node": self.last_registered_node
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
            
        print(f"FGDBを {filename} に保存しました")
        
    def load(self, filename="fgdb.pickle"):
        """
        FGDBデータをファイルから読み込み
        
        Args:
            filename (str): 読み込みファイル名
        """
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                
            self.management_graph = data["management_graph"]
            self.operation_graph = data["operation_graph"]
            self.blocks = data["blocks"]
            self.last_registered_node = data["last_registered_node"]
            
            print(f"FGDBを {filename} から読み込みました")
        else:
            print(f"ファイル {filename} が見つかりません")
            
    def get_statistics(self):
        """
        FGDB統計情報を取得
        
        Returns:
            dict: 統計情報
        """
        mg_nodes = self.management_graph.number_of_nodes()
        mg_edges = self.management_graph.number_of_edges()
        og_nodes = self.operation_graph.number_of_nodes()
        og_edges = self.operation_graph.number_of_edges()
        
        function_blocks = sum(1 for block in self.blocks.values() if block.get("category") == "function")
        data_blocks = sum(1 for block in self.blocks.values() if block.get("category") == "data")
        
        return {
            "management_graph": {"nodes": mg_nodes, "edges": mg_edges},
            "operation_graph": {"nodes": og_nodes, "edges": og_edges},
            "function_blocks": function_blocks,
            "data_blocks": data_blocks,
            "total_blocks": len(self.blocks)
        }
