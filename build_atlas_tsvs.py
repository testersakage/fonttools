import os
import sys
import glob
import re
import argparse

def build_integrated_tsv():
    parser = argparse.ArgumentParser(description="Luanti Font Atlas Integration TSV Builder")
    
    # 対象のフォルダ名（省略時は output_atlases_12px）
    parser.add_argument("dir", nargs="?", default="output_atlases_12px", 
                        help="Target directory containing .png.txt files")
    
    # オプション引数: -name でファイル名パターンを指定
    parser.add_argument("-name", "--name", default="atlas_12px_p%02X.png",
                        help="Atlas filename pattern. e.g. -name=\"unicode_page%%02x.png\"")
    
    args = parser.parse_args()
    target_dir = args.dir
    name_pattern = args.name
    output_tsv = "atlas_contents.tsv"

    print(f"【データ抽出開始】 フォルダ: '{target_dir}' | パターン: '{name_pattern}'")

    if not os.path.exists(target_dir):
        print(f"Error: フォルダ '{target_dir}' が見つかりません。")
        return

    # ★【バグ完全修正】Pythonの文字エスケープを修正。% は1個で探すのが正解でした。
    # ユーザーが指定したパターン文字列から、%02x などを安全にキャプチャグループに挿げ替えます。
    regex_pattern = re.escape(name_pattern)
    regex_pattern = re.sub(r'%02[xX]|%d', r'([0-9a-fA-F]{2})', regex_pattern)
    regex_pattern = regex_pattern + r'\.txt$'

    try:
        with open(output_tsv, "w", encoding="utf-8") as out_f:
            out_f.write("# code_point\tpage_hex\n")
            
            txt_files = sorted(glob.glob(os.path.join(target_dir, "*.png.txt")))
            
            if not txt_files:
                print(f"Error: '{target_dir}' 内に .png.txt ファイルが見つかりませんでした。")
                return

            total_valid_chars = 0

            for file_path in txt_files:
                base_name = os.path.basename(file_path)
                
                # 動的にビルドした正規表現で、正確にページ番号（16進数2桁）をスキャン
                match = re.search(regex_pattern, base_name, re.IGNORECASE)
                if not match:
                    continue # 命名規則に合致しないノイズファイルは安全にスルー
                
                page_hex = match.group(1).upper()

                with open(file_path, "r", encoding="utf-8") as in_f:
                    for line in in_f:
                        line = line.strip()
                        if not line or ":" not in line or "empty" in line or line.startswith("cell_size") or line.startswith("columns") or line.startswith("rows"):
                            continue
                        
                        code_point = line.split(":")
                        
                        # 0x20 などの短いHex表記が来ても、Lua側で一貫してパースしやすいよう、
                        # 最低4桁の綺麗な16進数（例: 0x0020）にゼロ埋め整形します。
                        raw_cp = code_point[0].upper().replace("0X", "")
                        if len(raw_cp) < 4:
                            raw_cp = raw_cp.zfill(4)
                        clean_cp = "0x" + raw_cp
                        
                        out_f.write(f"{clean_cp}\t{page_hex}\n")
                        total_valid_chars += 1

            print(f"【抽出完了】 統合ファイル '{output_tsv}' が正常に出力されました！")
            print(f"総有効文字数（アトラスに実在するフォント数）: {total_valid_chars} 文字")

    except Exception as e:
        print(f"書き込みエラーが発生しました: {e}")

if __name__ == "__main__":
    build_integrated_tsv()
