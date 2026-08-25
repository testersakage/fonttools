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
* **unifont_to_atlas.py**: GNU UnifontのChart画像を16列16行256枚のアトラス画像に変換します。

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
## 4. mcl_sign_to_atlas.py (mcl_signsからのアトラス生成)
Minecloniaの看板フォントの個別画像群を、12px仕様のアトラス画像へ一括変換・統合します。

## 📋 事前準備
1. Luantiのゲームディレクトリ（`games/mineclonia/mods/ITEMS/mcl_signs/` など）を開きます。
2. その中にある `textures/` フォルダを、本ツールのフォルダ（`fonttool/` 直下）に丸ごとコピーして配置してください。

## 💻 実行コマンド

```bash
python mcl_sign_to_atlas.py
```

------------------------------
## 5. build_atlas_tsvs.py (フォントマトリクスTSVの自動生成)
生成された `.png.txt`（フォント情報ファイル）群を一括スキャンし、メインフォントに「実在する文字」と「ページ番号」を記録した統合マトリクスTSVファイル（`unicode_main.tsv` 等）を自動ビルドします。
看板MOD側はこのリストを参照し、登録されていない文字（歯抜け部分）を自動的にサブアトラス（フォールバック先）へピンポイントで丸投げします。

## 📋 事前準備
1. `pmp_to_12px.py` などを使用し、あらかじめメインとなるアトラス画像群を生成しておきます。
2. 生成された出力フォルダの名前（例: `output_pixelmplus10`）と、出力されたアトラスのファイル名規則（例: `unicode_main%02x.png`）を確認します。

## 💻 実行コマンド

```bash
python build_atlas_tsvs.py <対象のフォルダ名> -name="<ファイル名規則>"
```
*💡 実行例：`python build_atlas_tsvs.py output_pixelmplus10 -name="unicode_main%02x.png"`*

※処理完了後、生成された `.tsv` ファイルの名前を設定に合わせてリネームし、`mod_mcl_signs/` の `init.lua` と同じ階層へ配置してください。




------------------------------
## 6. unifont_to_atlas.py (UnifontのChart画像をアトラスに変換)
[Unifoudry.com](https://unifoundry.com)にあるChat画像を16列16行256枚のアトラス画像に変換します。
[signs_lib mod](https://content.luanti.org/packages/mt-mods/signs_lib/) に同梱されているtextures/unifont/signs_lib_uni**.pngを日本語Chartに差し替えることで中華フォント問題を解消します。

## 📋 事前準備
1. 変換元となる`unifont_jp-<バージョン番号>.png` のコピーをunifont_to_atlas.pyと同じフォルダに置きます。
2. 変換元のファイル名と変換後の命名規則を確認します。
3. 変換の際に文字と背景の指定をします。黒地に白文字の場合は`--invert`オプションを付けてください。

## 💻 実行コマンド

```bash
python unifont_to_atlas.py <変換元ファイル名>.png --invert -n "<ファイル名><page>.png"
```
*💡 実行例：`python unifont_to_atlas.py unifont_jp-17.0.05.png --invert -n "signs_lib_uni<page>.png"`*

------------------------------
## 💻 動作環境

* Python 3.x
* 必須外部ライブラリ: Pillow (PIL)
※未導入の場合は pip install Pillow を実行してください。

------------------------------
## 📄 ライセンス

このMODは **MIT ライセンス** の下で公開されています。詳細は `LICENSE` ファイルを参照してください。

AI生成: このパッケージにはAIによって生成されたアセットまたはプログラムコードが含まれています。

