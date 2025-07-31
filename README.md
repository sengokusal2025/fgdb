# FGDB (Functional Graph DataBase)

関数実行履歴を管理するためのFunctional Graph DataBaseシステムです。

## 概要

FGDBは「y=f(x)」のような関数実行を追跡し、関数と変数の関係をグラフとして管理するシステムです。

### 主要機能

- **Management Graph (MG)**: 構成要素（関数・変数）の管理
- **Operation Graph (OG)**: 実行履歴の管理
- 関数ブロック(FB)とデータブロック(DB)の登録
- 関数実行の自動化
- グラフの可視化
- **NEW**: ハッシュコード形式での精密実行制御

## システム構成

### コアファイル

- `lib.py` - FGDBコアライブラリ
- `init.py` - システム初期化スクリプト
- `add_block.py` - ブロック登録スクリプト
- `operation.py` - 関数実行スクリプト
- `show_fgdb.py` - グラフ可視化スクリプト

### データ構造

```
fgdb3/
├── lib.py                    # コアライブラリ
├── init.py                   # 初期化スクリプト
├── add_block.py              # ブロック追加スクリプト
├── operation.py              # 実行スクリプト
├── show_fgdb.py              # 可視化スクリプト
├── fgdb.pickle              # データベースファイル
├── samples/                  # サンプルファイル
│   ├── f/                   # 関数ブロックサンプル
│   │   ├── func.py         # 関数実装
│   │   └── func.txt        # 関数説明
│   ├── x/                   # データブロックサンプル
│   │   └── data.csv        # データファイル
│   └── operation.txt        # 実行指示ファイル
└── {ハッシュコード}/          # 登録されたブロック
    ├── system.json          # ブロック情報
    ├── func.py (関数の場合)
    ├── func.txt (関数の場合)
    └── data.csv (データの場合)
```

## インストールと環境設定

### 必要なライブラリ

Python 3.7以上と以下のライブラリが必要です：

```bash
pip install -r requirements.txt
```

### 動作環境

- **Python**: 3.7以上
- **OS**: Windows/Linux/macOS
- **必須ライブラリ**: networkx, matplotlib

## 使用方法

### 1. システム初期化

```bash
python init.py
```

システムの初期化を実行し、以下の処理を行います：
- MGとOGのルートノードを作成
- `fgdb.pickle`ファイルを生成

### 2. ブロック登録

#### 関数ブロック追加
```bash
python add_block.py -f <function_folder>
```

#### データブロック追加
```bash
python add_block.py -d <data_folder>
```

### 3. 関数実行

```bash
python operation.py -i operation.txt
```

`operation.txt`の形式：

#### 名前形式（従来）
```
y=f(x)
```

#### ハッシュコード形式（新機能）
```
y=0f434271cf8dc290a2df15a3340bfbeca73a16daac6917120cb47f451f4e2b98(ebf7eb3432c8068da34906ebc39f4412bbb2708277498c9124add0cbf4f8a485)
```

**ハッシュコードの取得方法**:
1. `python show_fgdb.py` でブロック一覧を確認
2. 関数ブロックと入力データブロックのコードをコピー
3. `y=関数コード(入力データコード)` の形式で記述

### 4. グラフ可視化

```bash
python show_fgdb.py
```

## 新機能: ハッシュコード形式対応

version 1.1では、operation.txtでハッシュコードを直接指定できるようになりました。

### メリット
- **精密な制御**: 名称の重複を気にせず特定のブロックを指定
- **自動化対応**: スクリプトでハッシュコードを生成して実行
- **バージョン管理**: 実行履歴でどのバージョンを使用したか明確
- **後方互換性**: 既存の`y=f(x)`形式も完全サポート

### 使用例

```bash
# ブロック一覧を確認
python show_fgdb.py

# ハッシュコード形式でoperation.txtを作成
echo "y=0f434271...(ebf7eb34...)" > operation_hash.txt

# 実行
python operation.py -i operation_hash.txt
```

## 完全なワークフロー例

```bash
# 1. 初期化
python init.py

# 2. サンプル関数とデータの登録
python add_block.py -f samples/f
python add_block.py -d samples/x

# 3. 関数実行
copy samples/operation.txt operation.txt
python operation.py -i operation.txt

# 4. 結果の可視化
python show_fgdb.py
```

## ブロック仕様

### 関数ブロック (Function Block)

関数ブロックフォルダに含まれるファイル：
- `func.py` - 関数の実装（必須）
- `func.txt` - 関数の説明（推奨）

`func.py`の要件：
- コマンドライン引数 `-i <input_var>` と `-o <output_code>` を受け取る
- 入力変数名から対応するデータを読み込む
- 結果を出力コードのフォルダに保存する

### データブロック (Data Block)

データブロックフォルダに含まれるファイル：
- `data.csv` - データファイル（推奨）

## グラフ表示

### ノード形状
- **Root（ルート）**: ひし形（金色）
- **Function Block（関数ブロック）**: 矩形（スカイブルー）
- **Data Block（データブロック）**: 楕円（ペールグリーン）

### グラフ種類
- **Management Graph (MG)**: 登録順に要素を接続
- **Operation Graph (OG)**: 実行履歴を入力→出力の関係で表示

## サンプルファイル

### samples/f/func.py
数値を2倍にする関数のサンプル実装が含まれています。
- 入力値を数値として解析
- 2倍にして結果を出力
- エラーハンドリング付き

### samples/x/data.csv
初期値として「15」が設定されたデータファイルです。

### samples/operation.txt
基本的な実行形式「y=f(x)」の例が含まれています。

## トラブルシューティング

### よくある問題

1. **fgdb.pickleが見つからない**
   ```
   先にinit.pyを実行してください
   ```

2. **ブロックフォルダが見つからない**
   ```
   フォルダパスを確認してください
   ```

3. **関数実行エラー**
   ```
   func.pyの実装とoperation.txtの形式を確認してください
   ```

4. **日本語フォント警告**
   ```
   システムにインストールされている日本語フォントを使用します
   （機能に影響はありません）
   ```

## 技術仕様

### データ保存形式
- グラフデータ: pickle形式（`fgdb.pickle`）
- ブロック情報: JSON形式（`system.json`）
- データファイル: CSV形式（`data.csv`）

### ファイル説明

#### lib.py
- FGDBクラス：コア機能を提供
- ブロック管理機能
- グラフ操作機能
- データ保存・読み込み機能

#### add_block.py
- フォルダのコピーとハッシュ名変更
- system.json生成
- MGとOGへの登録

#### operation.py
- operation.txt解析
- バッチファイル生成と実行
- 実行結果のOG登録

#### show_fgdb.py
- NetworkXとMatplotlibによる可視化
- ノード形状の区別
- 統計情報表示

## 開発履歴

- **v1.0**: 基本的なFGDB機能の実装
- **v1.1**: ハッシュコード形式対応の追加

## ライセンス

このプロジェクトは教育目的で作成されました。

## 作者

Claude (Anthropic) により実装
