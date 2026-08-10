#!/usr/bin/env python3
import os
import sys
import shutil
import json
from PIL import Image, ImageDraw

# --- ランタイムデフォルト設定（JSON未指定時のフォールバック） ---
CONFIG = {
    "patch_dir": "./output_pixelmplus10",
    "patch_prefix": "unicode_page_",
    "patch_suffix": ".png",
    "base_dir": "./output_wqy_9pt",
    "base_prefix": "atlas_12px_p",
    "base_suffix": ".png",
    "output_dir": "./output_merged",
    "deny_area": []
}

def parse_range(range_str):
    """
    "0x0000-0x001F" や "32-127" などの文字列を (start_int, end_int) のタプルに変換する
    """
    range_str = range_str.strip().lower()
    if "-" not in range_str:
        return None
    
    start_str, end_str = range_str.split("-", 1)
    try:
        start_val = int(start_str, 16) if start_str.startswith("0x") else int(start_str)
        end_val = int(end_str, 16) if end_str.startswith("0x") else int(end_str)
        return start_val, end_val
    except ValueError:
        print(f"[!] Warning: マージ拒否エリアのパースに失敗しました: {range_str}")
        return None

def is_code_denied(code, deny_ranges):
    """コードポイントがマージ拒否エリアに含まれているか判定"""
    for start, end in deny_ranges:
        if start <= code <= end:
            return True
    return False

def parse_atlas_txt(txt_path):
    """*.png.txt を解析し、セル情報と各コードポイントの位置・統合可否を判定"""
    metrics = {"cell_w": 12, "cell_h": 12, "columns": 16, "rows": 16}
    glyph_coords = {}
    
    if not os.path.exists(txt_path):
        return None, None

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" in line and ":" not in line:
                key, val = line.split("=", 1)
                key = key.strip().lower()
                val_int = int(val.strip())
                if key == "cell_size" or key == "cell":
                    metrics["cell_w"] = val_int
                    metrics["cell_h"] = val_int
                elif "cell_size_w" in key or "cell_w" in key: metrics["cell_w"] = val_int
                elif "cell_size_h" in key or "cell_h" in key: metrics["cell_h"] = val_int
                elif "columns" in key: metrics["columns"] = val_int
                elif "rows" in key: metrics["rows"] = val_int
                continue
            
            if ":" in line:
                code_str, coord_str = line.split(":", 1)
                code_str = code_str.strip().lower()
                if code_str.startswith("0x"): code_str = code_str[2:]
                
                try: code_int = int(code_str, 16)
                except ValueError: continue
                
                if coord_str.lower() == "empty": continue
                if "," in coord_str:
                    try:
                        col, row = map(int, coord_str.split(",", 1))
                        glyph_coords[code_int] = (col, row)
                    except ValueError: continue
                        
    return metrics, glyph_coords

def load_config_args():
    global CONFIG
    # 引数から -config= を探してJSONを読み込む
    for arg in sys.argv[1:]:
        if arg.startswith("-config="):
            conf_path = arg.split("=", 1)[1].strip('"').strip("'")
            if os.path.exists(conf_path):
                try:
                    with open(conf_path, 'r', encoding='utf-8-sig') as f:
                        CONFIG.update(json.load(f))
                    print(f"[*] Config Loaded: {conf_path}")
                except Exception as e:
                    print(f"[!] Config Load Error: {e}")
                    sys.exit(1)
            else:
                print(f"[!] Error: Config file not found at {conf_path}")
                sys.exit(1)

def merge_atlases():
    load_config_args()

    dir_a = CONFIG["base_dir"]
    dir_b = CONFIG["patch_dir"]
    out_dir = CONFIG["output_dir"]

    print("\n" + "="*50)
    print(" Luanti Font Atlas Merger (Data-Driven Model) ")
    print("="*50)
    print(f" [A] Base Directory   : {dir_a}")
    print(f" [B] Patch Directory  : {dir_b}")
    print(f" [O] Output Directory : {out_dir}")
    print("-" * 50)

    if not os.path.exists(dir_a) or not os.path.exists(dir_b):
        print("[!] Error: 統合先(A) または 統合元(B) フォルダが見つかりません。")
        return

    # マージ拒否エリアのパース
    deny_ranges = []
    if CONFIG["deny_area"]:
        for r_str in CONFIG["deny_area"]:
            parsed = parse_range(r_str)
            if parsed:
                deny_ranges.append(parsed)
        print(f" [*] Active Deny Ranges: {CONFIG['deny_area']}")
        print("-" * 50)

    # 出力先フォルダの新規作成
    if os.path.exists(out_dir):
        try: shutil.rmtree(out_dir)
        except PermissionError:
            print("[!] Error: 出力フォルダがロックされています。ビューアーを閉じてください。")
            return
    os.makedirs(out_dir, exist_ok=True)

    # アトラス名の構築用拡張子（ドットの二重化を防ぐ）
    ext_a = "" if CONFIG["base_suffix"].startswith(".") else "."
    ext_b = "" if CONFIG["patch_suffix"].startswith(".") else "."

    for page in range(256):
        page_hex = f"{page:02X}"
        page_hex_lower = f"{page:02x}"
        
        # === JSON定義に基づくファイル名動的生成ルール ===
        # 統合先 (Base A) : 0xやブレを吸収するため、大文字小文字両パターンをチェック
        png_name_a = f"{CONFIG['base_prefix']}{page_hex}{ext_a}{CONFIG['base_suffix']}"
        txt_name_a = f"{png_name_a}.txt"
        path_a_png = os.path.join(dir_a, png_name_a)
        path_a_txt = os.path.join(dir_a, txt_name_a)
        
        if not os.path.exists(path_a_png): # 小文字パターンをセーフティチェック
            png_name_a = f"{CONFIG['base_prefix']}{page_hex_lower}{ext_a}{CONFIG['base_suffix']}"
            txt_name_a = f"{png_name_a}.txt"
            path_a_png = os.path.join(dir_a, png_name_a)
            path_a_txt = os.path.join(dir_a, txt_name_a)

        # 統合元 (Patch B)
        png_name_b = f"{CONFIG['patch_prefix']}{page_hex_lower}{ext_b}{CONFIG['patch_suffix']}"
        txt_name_b = f"{png_name_b}.txt"
        path_b_png = os.path.join(dir_b, png_name_b)
        path_b_txt = os.path.join(dir_b, txt_name_b)
        
        if not os.path.exists(path_b_png): # 大文字パターンをセーフティチェック
            png_name_b = f"{CONFIG['patch_prefix']}{page_hex}{ext_b}{CONFIG['patch_suffix']}"
            txt_name_b = f"{png_name_b}.txt"
            path_b_png = os.path.join(dir_b, png_name_b)
            path_b_txt = os.path.join(dir_b, txt_name_b)

        # 出力完成名 (O) は、A側の形式に統一
        path_o_png = os.path.join(out_dir, os.path.basename(path_a_png) if os.path.exists(path_a_png) else png_name_a)
        path_o_txt = os.path.join(out_dir, (os.path.basename(path_a_png) if os.path.exists(path_a_png) else png_name_a) + ".txt")
        # =================================================================

        # 統合元（Patch B）のデータが存在しない場合は、ベース（Base A）をそのまま出力先へコピー
        if not os.path.exists(path_b_png) or not os.path.exists(path_b_txt):
            if os.path.exists(path_a_png): shutil.copy(path_a_png, path_o_png)
            if os.path.exists(path_a_txt): shutil.copy(path_a_txt, path_o_txt)
            continue

        metrics_b, glyphs_b = parse_atlas_txt(path_b_txt)
        if not metrics_b or not glyphs_b:
            if os.path.exists(path_a_png): shutil.copy(path_a_png, path_o_png)
            if os.path.exists(path_a_txt): shutil.copy(path_a_txt, path_o_txt)
            continue

        cell_w = metrics_b["cell_w"]
        cell_h = metrics_b["cell_h"]
        cols = metrics_b["columns"]
        rows = metrics_b["rows"]

        if os.path.exists(path_a_png):
            img_a = Image.open(path_a_png).convert("RGBA")
        else:
            img_a = Image.new("RGBA", (cell_w * cols, cell_h * rows), (0, 0, 0, 0))

        img_b = Image.open(path_b_png).convert("RGBA")
        draw_a = ImageDraw.Draw(img_a)

        _, glyphs_a = parse_atlas_txt(path_a_txt)
        if glyphs_a is None: glyphs_a = {}

        start_code = page * 256
        merge_count = 0
        deny_count = 0

        for index in range(256):
            code = start_code + index
            
            if code in glyphs_b:
                # 【仕様追加】マージ拒否エリアに含まれているか厳密にチェック
                if is_code_denied(code, deny_ranges):
                    deny_count += 1
                    continue # 拒否エリア内の文字は統合せずスキップ（元のAの状態を維持）

                col_b, row_b = glyphs_b[code]
                src_x = col_b * cell_w
                src_y = row_b * cell_h

                col_a, row_a = index % cols, index // cols
                dst_x = col_a * cell_w
                dst_y = row_a * cell_h

                draw_a.rectangle([dst_x, dst_y, dst_x + cell_w - 1, dst_y + cell_h - 1], fill=(0, 0, 0, 0))

                glyph_box = (src_x, src_y, src_x + cell_w, src_y + cell_h)
                glyph_crop = img_b.crop(glyph_box)

                img_a.paste(glyph_crop, (dst_x, dst_y), glyph_crop)
                glyphs_a[code] = (col_a, row_a)
                merge_count += 1

        img_a.save(path_o_png, "PNG")

        out_txt_lines = [f"cell_size_w={cell_w}\n", f"cell_size_h={cell_h}\n", f"columns={cols}\n", f"rows={rows}\n"]
        for index in range(256):
            code = start_code + index
            if code in glyphs_a:
                col_o, row_o = glyphs_a[code]
                out_txt_lines.append(f"{hex(code)}:{col_o},{row_o}\n")
            else:
                out_txt_lines.append(f"{hex(code)}:empty\n")

        with open(path_o_txt, "w", encoding="utf-8") as f:
            f.writelines(out_txt_lines)

        if merge_count > 0:
            deny_msg = f" (拒否ガード {deny_count}文字)" if deny_count > 0 else ""
            print(f" [*] Merged: {os.path.basename(path_a_png)} <- {os.path.basename(path_b_png)} ({merge_count}文字を統合){deny_msg}")

    print("-" * 50)
    print(f" [!] All processing completed. Final files saved in: {out_dir}")
    print("="*50)

if __name__ == "__main__":
    merge_atlases()
