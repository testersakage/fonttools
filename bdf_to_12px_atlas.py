import os
from PIL import Image

def parse_bdf_font(bdf_path):
    """BDFファイルをパースして、Unicodeコードポイントをキーとするビットマップ辞書を返す"""
    font_map = {}
    print("9pt BDFファイルの読み込み中... (数秒かかります)")
    if not os.path.exists(bdf_path):
        print(f"Error: {bdf_path} が見つかりません。")
        return font_map

    with open(bdf_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    current_code = None
    bbx_w, bbx_h, bbx_x, bbx_y = 0, 0, 0, 0
    in_bitmap = False
    bitmap_rows = []

    for line in lines:
        line = line.strip()
        if line.startswith("ENCODING"):
            current_code = int(line.split()[1])
            bitmap_rows = []
        elif line.startswith("BBX"):
            parts = line.split()
            bbx_w = int(parts[1])
            bbx_h = int(parts[2])
            bbx_x = int(parts[3])
            bbx_y = int(parts[4])
        elif line.startswith("BITMAP"):
            in_bitmap = True
        elif line.startswith("ENDCHAR"):
            in_bitmap = False
            if current_code is not None and 0 <= current_code <= 0xFFFF:
                byte_list = []
                for row in bitmap_rows:
                    if len(row) == 2:
                        byte_list.append(int(row, 16))
                    elif len(row) == 4:
                        byte_list.append(int(row[:2], 16))
                        byte_list.append(int(row[2:], 16))
                    else:
                        val = int(row, 16)
                        if val < 256:
                            byte_list.append(val)
                        else:
                            byte_list.append((val >> 8) & 0xFF)
                            byte_list.append(val & 0xFF)
                
                font_map[current_code] = {
                    "bytes": bytes(byte_list),
                    "w": bbx_w,
                    "h": bbx_h,
                    "x": bbx_x,
                    "y": bbx_y
                }
            current_code = None
        elif in_bitmap:
            bitmap_rows.append(line)
            
    return font_map

def generate_9pt_12px_atlases(bdf_path):
    font_map = parse_bdf_font(bdf_path)
    if not font_map:
        return

    output_dir = "output_atlases_12px"
    os.makedirs(output_dir, exist_ok=True)

    # 1文字の枠を「12x12px」にします
    cell_size = 12
    columns = 16
    rows = 16
    atlas_w = columns * cell_size
    atlas_h = rows * cell_size

    # 9pt（およそ漢字が9x9pxで、全体が11〜12px以下に収まる想定）の
    # ベースライン位置をマスの下部から何ピクセル上にするかをロックします。
    # 通常、9pt（サイズ9〜11）のフォントは下から2〜3px目をベースラインにすると美しく整列します。
    ascent_baseline_y = 9 

    print(f"【処理開始】1マス: {cell_size}x{cell_size}px (画像サイズ: {atlas_w}x{atlas_h}px)")
    print(f"0x00 から 0xFF まで全256ページを完全出力します。")

    for page in range(256):
        start_code = page * 256
        page_hex = f"{page:02X}"
        
        atlas_img = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
        output_txt_lines = [f"cell_size={cell_size}\ncolumns={columns}\nrows={rows}\n"]

        for row in range(rows):
            for col in range(columns):
                code = start_code + (row * columns) + col
                dst_x = col * cell_size
                dst_y = row * cell_size
                
                if code in font_map:
                    c_data = font_map[code]
                    char_img = Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0))
                    
                    byte_width = 1 if c_data["w"] <= 8 else 2
                    
                    # === 【バグ修正】BDFのBBX位置を考慮した絶対ベースライン配置ロジック ===
                    # 横方向：マスの中央付近に文字のBBX原点が来るようにオフセットを設定
                    offset_x = (cell_size - c_data["w"]) // 2

                    # 縦方向：BDF規格のベースライン相対y座標（c_data["y"]）を使用
                    # 12pxマスの「ascent_baseline_y」のラインを基準線として、
                    # そこから文字の高さ（h）とBDFのyオフセットを計算して最上段（y=0）からのドロップ位置を特定します。
                    offset_y = ascent_baseline_y - c_data["h"] - c_data["y"]
                    
                    # 異常なフォントデータによる配列外はみ出しを防ぐセーフティガード
                    if offset_y < 0: offset_y = 0
                    if offset_y >= cell_size: offset_y = cell_size - 1
                    # ===================================================================

                    for y_idx in range(len(c_data["bytes"]) // byte_width):
                        if byte_width == 1:
                            byte_val = c_data["bytes"][y_idx]
                            bits = f"{byte_val:08b}"
                        else:
                            b1 = c_data["bytes"][y_idx * 2]
                            b2 = c_data["bytes"][y_idx * 2 + 1]
                            bits = f"{b1:08b}{b2:08b}"
                        
                        for x_idx in range(c_data["w"]):
                            if x_idx < len(bits) and bits[x_idx] == "1":
                                px = offset_x + x_idx
                                py = offset_y + y_idx
                                if 0 <= px < cell_size and 0 <= py < cell_size:
                                    char_img.putpixel((px, py), (255, 255, 255, 255))
                    
                    atlas_img.paste(char_img, (dst_x, dst_y))
                    output_txt_lines.append(f"{hex(code)}:{col},{row}\n")
                else:
                    output_txt_lines.append(f"{hex(code)}:empty\n")

        file_base = f"atlas_wqy9_p{page_hex}"
        png_path = os.path.join(output_dir, file_base + ".png")
        txt_path = os.path.join(output_dir, file_base + ".png.txt")
        
        atlas_img.save(png_path, "PNG")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.writelines(output_txt_lines)

    print(f"\n【すべて完了しました！】")
    print(f"成果物は '{output_dir}' フォルダ内に正しいベースライン位置で保存されました。")

if __name__ == "__main__":
    bdf_filename = "wenquanyi_9pt.bdf" 
    if os.path.exists("wenquanyi_9pt.bdf"):
        bdf_filename = "wenquanyi_9pt.bdf"
    generate_9pt_12px_atlases(bdf_filename)
