# unifont_to_atlas.py

import os
import argparse
from PIL import Image

def process_atlas_colors(img):
    """
    白背景・黒文字の画像を「黒背景・白文字（文字部分は完全透過）」に修正
    """
    # 確実にRGBAモードに変換
    rgba_img = img.convert("RGBA")
    datas = rgba_img.getdata()
    
    new_data = []
    for item in datas:
        # カラー画像やグレー画像に対応できるようRGBの平均値を計算
        if isinstance(item, tuple):
            brightness = (item[0] + item[1] + item[2]) // 3
        else:
            brightness = item
            
        # 【修正された反転・透過ロジック】
        # 元が白（輝度255） -> RGBを (0,0,0) の黒にして、アルファを 255 (完全不透明)
        # 元が黒（輝度0）   -> RGBを (255,255,255) の白にして、アルファを 0 (完全透過)
        
        new_r = 255 - brightness  # 輝度を反転（元白255→0、元黒0→255）
        new_g = 255 - brightness
        new_b = 255 - brightness
        new_a = brightness        # 元白255→255(不透明)、元黒0→0(透過)
        
        new_data.append((new_r, new_g, new_b, new_a))
        
    rgba_img.putdata(new_data)
    return rgba_img

def split_unifont_to_atlases(input_image_path, output_dir="output_atlases", 
                             invert_and_transparent=False, outname_pattern="atlas_<page>.png",
                             offset_x=32, offset_y=64):
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        img = Image.open(input_image_path)
    except FileNotFoundError:
        print(f"エラー: 入力画像 '{input_image_path}' が見つかりません。")
        return
    
    width, height = img.size
    print(f"入力画像のサイズ: {width}x{height}")
    print(f"読み取り開始オフセット: X={offset_x}, Y={offset_y}")
    
    glyph_size = 16
    glyphs_per_page = 256 
    atlas_grid_size = 16   
    atlas_pixel_size = glyph_size * atlas_grid_size 
    
    total_pages = (height - offset_y) // glyph_size
    if total_pages > 256:
        total_pages = 256  
        
    print(f"アトラス生成を開始します（1列の256文字を16x16に並び替え）: 計 {total_pages}枚")
    
    for page_idx in range(total_pages):
        # 並び替え用の土台キャンバス（RGB）
        canvas = Image.new("RGB", (atlas_pixel_size, atlas_pixel_size), "white")
        
        src_y = offset_y + (page_idx * glyph_size)
        
        for glyph_idx in range(glyphs_per_page):
            src_x = offset_x + (glyph_idx * glyph_size)
            
            if src_x + glyph_size > width or src_y + glyph_size > height:
                continue
                
            glyph_img = img.crop((src_x, src_y, src_x + glyph_size, src_y + glyph_size))
            
            dst_col = glyph_idx % atlas_grid_size  
            dst_row = glyph_idx // atlas_grid_size 
            
            dst_x = dst_col * glyph_size
            dst_y = dst_row * glyph_size
            
            canvas.paste(glyph_img, (dst_x, dst_y))
            
        # 土台を並び終えた後に、色反転とアルファ設定を同時に行う
        if invert_and_transparent:
            canvas = process_atlas_colors(canvas)
        
        hex_page = f"{page_idx:02X}"
        
        if "<page>" in outname_pattern:
            filename = outname_pattern.replace("<page>", hex_page)
        else:
            filename = f"{outname_pattern}_{hex_page}"
        
        if not filename.lower().endswith(".png"):
            filename += ".png"
        
        output_path = os.path.join(output_dir, filename)
        canvas.save(output_path)

    print(f"完了しました！ '{output_dir}' フォルダに {total_pages} 枚の並び替え済みアトラス画像を保存しました。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GNU Unifontの画像（横1列256文字）を、16x16の正方形アトラス256枚に並び替えて分割します。")
    
    parser.add_argument("input_file", help="変換元の画像ファイル名")
    parser.add_argument("-o", "--output", default="output_atlases", help="出力先フォルダ名")
    parser.add_argument("--invert", action="store_true", help="黒背景・白文字（文字部分100%%透過）に変換する")
    parser.add_argument("-n", "--outname", default="atlas_<page>.png", help="出力ファイル名の規則")
    
    parser.add_argument("-x", "--offset_x", type=int, default=32, help="読み取り開始位置のX座標 (デフォルト: 32)")
    parser.add_argument("-y", "--offset_y", type=int, default=64, help="読み取り開始位置のY座標 (デフォルト: 64)")
    
    args = parser.parse_args()
    
    split_unifont_to_atlases(
        input_image_path=args.input_file,
        output_dir=args.output,
        invert_and_transparent=args.invert,
        outname_pattern=args.outname,
        offset_x=args.offset_x,
        offset_y=args.offset_y
    )
