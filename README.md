## 🛠️ Font Tools (Luanti Font Atlas Utilities)

- [English Documentation (README.en.md)](./README.en.md)

Luanti（旧Minetest）のカスタムフォント開発における、フォントアトラス（Atlas）画像の生成・パッチ・合成を自動化する単体動作型のPythonスクリプト集です。
------------------------------
## 📦 同梱スクリプト一覧

* **bdf_to_12px.py**: wenquanyi_9pt.bdf から12px等幅仕様の完璧なアトラス画像を自動生成します（ベースライン補正ロジック内蔵）。
* **pmp_to_12px.py**: PixelMplus10-Regular.ttf から12px等幅アトラス画像を自動生成します。
* **atlas_merge.py**: 2つの異なるフォントアトラスを1つに高精度で自動合成（マージ）します。
* **mcl_sign_to_atlas.py**: Minecloniaの看板用フォントをアトラス画像に変換します。
* **build_atlas_tsvs.py**: アトラス生成時に出力されるテキストからtsv形式のフォントリストを作成します。

------------------------------
## 🛠️ 導入方法

1. このリポジトリをZIP形式でダウンロードするか、gitを使用してクローンします。
2. 展開したフォルダを、適当な場所に展開します。
3. フォルダ名を正確に **`fonttools`** に変更します。

------------------------------
## 🚀 各スクリプトの使用方法

## 1. bdf_to_12px.py (BDFからのアトラス生成)
ベースライン（文字の地面）を数学的に完全補正し、小文字や半角カナ（ｧｨｩｪｫ等）の上下のズレを綺麗に整列させて12pxアトラスを出力します。
## 📋 事前準備

   1. あらかじめ wenquanyi_9pt.bdf をダウンロードします。(https://sourceforge.net/projects/wqy/)
   2. スクリプトと同じフォルダ（fonttools/ 直下）に配置してください。

## 💻 実行コマンド

```bash
python bdf_to_12px.py
```

※出力先フォルダ（output_atlases_12px/）は自動的に生成されます。
------------------------------
## 2. pmp_to_12px.py (TTFからのアトラス生成)
※主に中華フォントの文字化け・すり替え問題（いわゆる中華フォント問題）を解決するための日本語環境向けスクリプトです。日本語環境以外では必須ではありません。
## 📋 事前準備

   1. あらかじめ PixelMplus10-Regular.ttf をダウンロードします。(https://github.com/itouhiro/PixelMplus)
   2. スクリプトと同じフォルダ（fonttools/ 直下）に配置してください。

## 💻 実行コマンド

```bash
python pmp_to_12px.py -config="px_mplus10.json"
```

※出力先などの詳細な設定は、同梱の px_mplus10.json から自由にカスタマイズ可能です。
------------------------------
## 3. atlas_merge.py (アトラスの合成パッチ処理)
2種類のアトラス画像を統合し、フォントを拡張・パッチします。用途に合わせて以下の設定ファイルを指定して実行してください。
## 💡 パターンA：Pixel Mplus フォントをパッチする場合

```bash
python atlas_merge.py -config="merge_pmp.json"
```

※出力設定は merge_pmp.json で変更可能です。
## 💡 パターンB：MCL Signs（看板用）をパッチする場合

   1. 『Standalone MCL Signs MOD』側で mcl_sign_to_atlas.py を実行し、アトラス画像を生成します。
   2. 生成された出力フォルダを、そのまま本ツールのフォルダ（fonttools/ 直下）に配置してください。
   3. 以下のコマンドを実行します。

```bash
python atlas_merge.py -config="merge_mcl.json"
```

※出力設定は merge_mcl.json で変更可能です。
------------------------------
## 4. mcl_sign_to_atlas.py
------------------------------
## 5. build_atlas_tsvs.py
------------------------------
## 💻 動作環境

* Python 3.x
* 必須外部ライブラリ: Pillow (PIL)
※未導入の場合は pip install Pillow を実行してください。

------------------------------
## 📄 ライセンス

このMODは **MIT ライセンス** の下で公開されています。詳細は `LICENSE` ファイルを参照してください。

AI生成: このパッケージにはAIによって生成されたアセットまたはプログラムコードが含まれています。

