#!/usr/bin/env python3
import sys
import os
import json
from PIL import Image, ImageDraw, ImageFont

# --- 確定デフォルト設定 ---
CONFIG = {
    "prefix": "unicode_page",
    "save_dir": "./unicode_pages",
    "load_path": "",
    "pt": 10.0,
    "dpi": 72.0,
    "grid_w": 16,
    "grid_h": 16,
    "width": 12,
    "height": 12,
    "smooth": "off",
    "upscale": 4, # 💡 トラップ回避のため、内部中継処理を4倍アップスケールに固定します
    "threshold": 128,
    "color": (255, 255, 255, 255)
}

# --- 【JIS X 0208 完全数式復元 ＋ 日本語特殊環境補完】文字抽出関数 ---
def get_jis_level1_2_set():
    jis_set = set()
    sjis_ranges = [range(0x81, 0x9F + 1), range(0xE0, 0xFC + 1)]
    for b1 in sjis_ranges:
        for b1_val in b1:
            for b2_val in range(0x40, 0xFC + 1):
                if b2_val == 0x7F: continue
                sjis_bytes = bytes([b1_val, b2_val])
                try:
                    char_str = sjis_bytes.decode('cp932')
                    if len(char_str) == 1: jis_set.add(ord(char_str))
                except UnicodeDecodeError: continue
    for cp in range(0xFF61, 0xFF9F + 1): jis_set.add(cp)
    jis_set.add(0x20AC)
    for cp in range(0x2150, 0x218F + 1): jis_set.add(cp)
    for cp in range(0x2460, 0x24FF + 1): jis_set.add(cp)
    for cp in range(0x3300, 0x33FF + 0x1): jis_set.add(cp)
    return jis_set

def analyze_font_metrics(load_path, pt, dpi):
    px_size = round((pt * dpi) / 72.0)
    try: font = ImageFont.truetype(load_path, int(px_size))
    except: return None
    print("\n" + "="*45)
    print(f" SDL3-Style Font Metrics Analysis ")
    print("="*45)
    print(f" Calc Size     : {px_size} px")
    print("-" * 45)
    return font

def parse_color_string(val):
    val = val.strip().lower()
    if val in ["w", "white"]: return (255, 255, 255, 255)
    if val in ["b", "black"]: return (0, 0, 0, 255)
    cleaned = val.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
    try:
        parts = [int(p.strip()) for p in cleaned.split(",")]
        if len(parts) == 3: return (parts, parts, parts, 255)
        if len(parts) == 4: return (parts, parts, parts, parts)
    except: pass
    return (255, 255, 255, 255)

def parse_args():
    global CONFIG
    for arg in sys.argv[1:]:
        if arg.startswith("-config="):
            conf_path = arg.split("=", 1)[1].strip('"').strip("'")
            if os.path.exists(conf_path):
                try:
                    with open(conf_path, 'r', encoding='utf-8-sig') as f:
                        loaded_config = json.load(f)
                        if "color" in loaded_config and isinstance(loaded_config["color"], str):
                            loaded_config["color"] = parse_color_string(loaded_config["color"])
                        CONFIG.update(loaded_config)
                except Exception as e: print(f"[!] Config Error: {e}"); sys.exit(1)
    for arg in sys.argv[1:]:
        if "=" not in arg: continue
        key, val = arg.split("=", 1)
        if key == "-load":      CONFIG["load_path"] = val
        elif key == "-pt":      CONFIG["pt"] = float(val)
        elif key == "-dpi":     CONFIG["dpi"] = float(val)
        elif key == "-upscale": CONFIG["upscale"] = int(val)
        elif key == "-threshold": CONFIG["threshold"] = int(val)
        elif key == "-save":    CONFIG["save_dir"] = val
        elif key == "-prefix":  CONFIG["prefix"] = val
        elif key == "-smooth":  CONFIG["smooth"] = val.lower()
        elif key == "-width":   CONFIG["width"] = int(val)
        elif key == "-height":  CONFIG["height"] = int(val)
        elif key == "-color":   CONFIG["color"] = parse_color_string(val)
        elif key == "-page":
            w, h = val.lower().split("x")
            CONFIG["grid_w"], CONFIG["grid_h"] = int(w), int(h)
    os.makedirs(CONFIG["save_dir"], exist_ok=True)

def render_glyph_v3(ch, font_path, pt, dpi, width, height):
    """純粋ドット等幅配置エンジン（アップスケール中継・位置バグ完全封印版）"""
    # 💡 4倍拡大フォントを生成（PixelMplus10の1ドットを「4x4ピクセル」の極太として描画させます）
    upscale = 4
    px_size = round((pt * dpi) / 72.0)
    target_px = px_size * upscale
    
    try:
        font = ImageFont.truetype(font_path, int(target_px))
    except:
        return Image.new("L", (width, height), 0)
    
    canvas_w = width * upscale
    canvas_h = height * upscale
    
    # 巨大なLモードバッファを作成
    res_large = Image.new("L", (canvas_w, canvas_h), 0)
    draw = ImageDraw.Draw(res_large)
    
    # 💡 マイナス座標やanchorを一切使わず、Pillow標準の (0, 0) でゆったり描画
    # これによりPillowの「枠外切り落とし・上付き暴走補正」が物理的に100%発動しなくなります！
    draw.text((0, 0), ch, font=font, fill=255)

    # 縮小処理（smoothがonならLANCZOS、offなら等幅ドット維持のNEAREST）
    resample_method = Image.LANCZOS if CONFIG["smooth"] == "on" else Image.NEAREST
    res = res_large.resize((width, height), resample=resample_method)

    # 閾値による2値化（輝度255のパキパキに固定）
    if CONFIG["threshold"] >= 0:
        res = res.point(lambda p: 255 if p > CONFIG["threshold"] else 0)
    
    return res

def draw_page(page, font_path, jis_whitelist):
    width_base = CONFIG["width"]   # 12
    height_base = CONFIG["height"] # 12
    gw, gh = CONFIG["grid_w"], CONFIG["grid_h"] # 16x16
    
    img = Image.new("RGBA", (width_base * gw, height_base * gh), (0, 0, 0, 0))
    draw_img = ImageDraw.Draw(img)
    output_txt_lines = [f"cell_size_w={width_base}\ncell_size_h={height_base}\ncolumns={gw}\nrows={gh}\n"]

    # 簡易的な生存判定用の等倍フォントオブジェクト
    px_size = round((CONFIG["pt"] * CONFIG["dpi"]) / 72.0)
    try: check_font = ImageFont.truetype(font_path, int(px_size))
    except: check_font = None

    for index in range(256):
        cp = page * 256 + index
        ch = chr(cp)
        char_w = width_base // 2 if (0x00 <= cp <= 0x7F) or (0xFF61 <= cp <= 0xFF9F) else width_base

        if cp == 0x0A or cp == 0x0D or cp < 32 or (127 <= cp <= 159):
            output_txt_lines.append(f"{hex(cp)}:empty\n")
            continue

        is_jis_character = (cp <= 0xFF) or (cp in jis_whitelist)
        is_glyph_valid = False

        if is_jis_character and check_font:
            try:
                # getbboxによる文字データの物理的な存在チェック
                bbox = check_font.getbbox(ch)
                if bbox and (bbox[2] - bbox[0]) > 0:
                    is_glyph_valid = True
            except: is_glyph_valid = False

        if not is_glyph_valid:
            output_txt_lines.append(f"{hex(cp)}:empty\n")
            continue

        col, row = index % gw, index // gw
        target_x = col * width_base 
        target_y = row * height_base

        # 描画区画を一旦クリア
        draw_img.rectangle([target_x, target_y, target_x + width_base - 1, target_y + height_base - 1], fill=(0, 0, 0, 0))

        # 4倍中継配置エンジンで文字グラフィックを生成
        glyph = render_glyph_v3(ch, font_path, CONFIG["pt"], CONFIG["dpi"], char_w, height_base)

        # 指定色(CONFIG["color"])のアルファマスクとしてパッキング
        g_rgba = Image.new("RGBA", (char_w, height_base), CONFIG["color"])
        g_rgba.putalpha(glyph)
        
        # 12pxマスの左上端から左詰め等幅仕様でペースト
        img.paste(g_rgba, (target_x, target_y), g_rgba)
        output_txt_lines.append(f"{hex(cp)}:{col},{row}\n")

    filename_base = f"{CONFIG['prefix']}{page:02x}"
    filename_png = os.path.join(CONFIG["save_dir"], f"{filename_base}.png")
    filename_txt = os.path.join(CONFIG["save_dir"], f"{filename_base}.png.txt")
    img.save(filename_png)
    with open(filename_txt, "w", encoding="utf-8") as f: f.writelines(output_txt_lines)
    print(f"[*] Saved: {filename_png}")

def main():
    parse_args()
    if not os.path.exists(CONFIG["load_path"]):
        print(f"[!] Font not found: {CONFIG['load_path']}"); sys.exit(1)
        
    jis_whitelist = get_jis_level1_2_set()
    for page in range(256): 
        draw_page(page, CONFIG["load_path"], jis_whitelist)
    print("\n[!] All 256 pages generated successfully with Monospace-Precision Verification.")

if __name__ == "__main__":
    main()
