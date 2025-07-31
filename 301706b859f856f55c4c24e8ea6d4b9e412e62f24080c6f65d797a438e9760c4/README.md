# データ処理システム

このプロジェクトは、CSVファイルからデータを読み込み、指定された関数 `f(x) = -5*x + 1` を適用して結果を出力するPythonシステムです。

## 仕様

### 機能概要
1. 指定入力フォルダ下の `data.csv` を読み込み
2. 読み込んだデータ `x` に関数 `f(x) = -5*x + 1` を適用
3. 結果 `y` を指定出力フォルダ下の `data.csv` に保存
4. 出力ファイルを読み込んで表示する機能を提供

### ファイル構成
```
project/
├── func.py          # メイン処理スクリプト
├── lib.py           # ライブラリ関数（読み込み・表示）
├── main.py          # テストコード
├── README.md        # このファイル
└── requirements.txt # 依存関係
```

## 使用方法

### 基本実行
```bash
python func.py -i <input_folder> -o <output_folder>
```

### 引数説明
- `-i, --input`: 入力フォルダのパス（`data.csv`を含む）
- `-o, --output`: 出力フォルダのパス（結果の`data.csv`を保存）

### 実行例
```bash
python func.py -i ./input_data -o ./output_data
```

## CSVファイル形式

### 入力ファイル（`data.csv`）
```
data
1
3
56
23
664
```

### 出力ファイル（`data.csv`）
```
data
-4
-14
-279
-114
-3319
```

## モジュール詳細

### func.py
- **apply_function(x)**: 関数 `f(x) = -5*x + 1` を適用
- **process_data(input_folder, output_folder)**: データ処理のメイン機能
- **main()**: コマンドライン引数の処理とメイン実行

### lib.py
- **read_csv_file(file_path)**: CSVファイルを読み込んでデータリストを返す
- **display_csv_data(file_path)**: CSVファイルの内容を標準出力に表示
- **read_output_folder_csv(output_folder)**: 出力フォルダのCSVを読み込んで表示
- **get_data_summary(file_path)**: データの統計情報を取得

### main.py
テストスイートとして以下の機能を提供：
- 関数の動作テスト
- テストデータの生成
- 完全なデータ処理フローのテスト
- ライブラリ関数のテスト

## テスト実行

### 完全テストの実行
```bash
python main.py
```

### ライブラリ関数の個別テスト
```bash
python lib.py <csv_file_path>
```

## エラーハンドリング

システムは以下のエラーケースに対処します：
- 入力ファイルが存在しない場合
- 無効なデータ形式
- 出力フォルダの作成権限がない場合
- 数値変換エラー

## 依存関係

- Python 3.6以上
- 標準ライブラリのみ使用（追加パッケージ不要）

## 注意事項

1. 入力CSVファイルは `data.csv` という名前である必要があります
2. CSVファイルの最初の行がヘッダー（`data` または `x`）の場合、自動的にスキップされます
3. 数値以外のデータは警告と共にスキップされます
4. 出力フォルダが存在しない場合、自動的に作成されます

## 開発・拡張

新しい関数を追加する場合は、`func.py`の`apply_function`を変更し、対応するテストを`main.py`に追加してください。
