## 🛠️ Font Tools (Luanti Font Atlas Utilities)

- [Japanese Documentation (README.md)](./README.md)

A standalone collection of Python utility scripts designed to automate the generation, patching, and merging of font atlas images for custom font development in **Luanti** (formerly Minetest).

------------------------------
## 📦 Bundled Scripts

* **`bdf_to_12px.py`**: Automatically generates perfect 12px monospaced font atlas images from `wenquanyi_9pt.bdf` (features built-in mathematical baseline alignment correction).
* **`pmp_to_12px.py`**: Automatically generates 12px monospaced font atlas images from `PixelMplus10-Regular.ttf`.
* **`atlas_merge.py`**: Merges two different font atlases into a single, high-precision combined atlas image.
* **`mcl_sign_to_atlas.py`**: Converts Mineclonia sign fonts into an atlas image.
* **`build_atlas_tsvs.py`**: Creates a font list in TSV format from the text output during atlas generation.

------------------------------
## 🛠️ Installation

1. Download this repository as a `.ZIP` file or clone it using git.
2. Extract the downloaded folder to a directory of your choice.
3. Ensure the extracted folder name is strictly and accurately renamed to **`fonttools`**.

------------------------------
## 🚀 How to Use the Scripts

## 1. bdf_to_12px.py (Atlas Generation from BDF) https://sourceforge.net/projects/wqy/
Mathematically corrects the baseline (the textual ground-level) to perfectly align smaller characters and half-width Japanese Katakana (e.g., ｧｨｩｪｫ) vertically, outputting cleanly organized 12px font atlases.

## 📋 Prerequisites
1. Download the `wenquanyi_9pt.bdf` file beforehand.
2. Place it directly inside the same folder as the script (`fonttools/` root).

## 💻 Execution Command
```bash
python bdf_to_12px.py
```
*※The output destination directory (`output_atlases_12px/`) will be generated automatically.*

------------------------------
## 2. pmp_to_12px.py (Atlas Generation from TTF) https://github.com/itouhiro/PixelMplus
*Note: This script is primarily intended for Japanese users to resolve font substitution/fallback issues (the so-called "Han Unification / Chinese font fallback problem"). It is optional for non-Japanese environments.*

## 📋 Prerequisites
1. Download the `PixelMplus10-Regular.ttf` file beforehand.
2. Place it directly inside the same folder as the script (`fonttools/` root).

## 💻 Execution Command
```bash
python pmp_to_12px.py -config="px_mplus10.json"
```
*※Output paths and detailed properties can be customized freely via the bundled `px_mplus10.json` config file.*

------------------------------
## 3. atlas_merge.py (Atlas Merging & Patching Process)
Integrates two different font atlas variations to expand and patch font sheets. Run the script by specifying one of the following configuration files based on your intended usage.

## 💡 Profile A: Patching the Pixel Mplus Font
```bash
python atlas_merge.py -config="merge_pmp.json"
```
*※Output configurations can be adjusted inside `merge_pmp.json`.*

## 💡 Profile B: Patching MCL Signs (For Signboards)
1. Run `mcl_sign_to_atlas.py` on the "Standalone MCL Signs Mod" side to generate the baseline font atlases.
2. Copy the resulting output directory and paste it directly into this utility's folder (`fonttool/` root).
3. Execute the following command:

```bash
python atlas_merge.py -config="merge_mcl.json"
```
*※Output configurations can be adjusted inside `merge_mcl.json`.*

------------------------------
## 4. mcl_sign_to_atlas.py (Atlas Generation from mcl_signs)
Converts and solidifies the discrete signboard font images from Mineclonia into a single set of 12px font atlas textures.

## 📋 Prerequisites
1. Navigate to your Luanti game directory (e.g., `games/mineclonia/mods/ITEMS/mcl_signs/`).
2. Copy the entire `textures/` directory and paste it directly into this utility's folder (`fonttool/` root).

## 💻 Execution Command

```bash
python mcl_sign_to_atlas.py
```

------------------------------
## 5. build_atlas_tsvs.py (Font Matrix TSV Code-point Builder)
Scans all generated `.png.txt` font description files to automatically build a unified matrix TSV file (e.g., `unicode_main.tsv`) that registers all "existing characters" and their respective page numbers.
The signboard mod references this list during runtime; any character not registered in this matrix (missing/blank glyphs) is dynamically routed to the secondary fallback sub-atlas.

## 📋 Prerequisites
1. Generate your primary font atlas beforehand using `pmp_to_12px.py` or a similar script.
2. Note the exact name of the generated output directory (e.g., `output_pixelmplus10`) and its atlas file naming convention (e.g., `unicode_main%02x.png`).

## 💻 Execution Command
```bash
python build_atlas_tsvs.py <folder_name> -name="<filename_pattern>"
```
*💡 Example:* `python build_atlas_tsvs.py output_pixelmplus10 -name="unicode_main%02x.png"`

*Note: Once the process is complete, rename the resulting `.tsv` file to match your mod configurations, and place it directly inside the `mod_mcl_signs/` directory alongside `init.lua`.*

------------------------------
## 6. unifont_to_atlas.py (Convert Unifont Chart Images to Font Atlases)
Converts a single Unifont Chart image obtained from [Unifoudry.com](https://unifoundry.com) into 256 individual page atlas images formatted in a 16x16 grid structure. 
By replacing the vanilla textures (`textures/unifont/signs_lib_uni<page>.png`) found inside the [signs_lib mod](https://content.luanti.org/packages/mt-mods/signs_lib/) with the generated localized Japanese chart pages, you can completely eliminate CJK Han unification display issues (commonly known as the default Chinese font bug).

## Prerequisites
1. Place a copy of your source `unifont_jp-<version>.png` image inside the same directory as `unifont_to_atlas.py`.
2. Confirm the exact input filename and your desired naming convention pattern for the output files.
3. Configure the foreground (text) and background color mappings during conversion. If the source image features white text on a black background, you must append the `--invert` option flag.

## Execution Command

```bash
python unifont_to_atlas.py <source_filename>.png --invert -n "<output_prefix><page>.png"
```
*Example: `python unifont_to_atlas.py unifont_jp-17.0.05.png --invert -n "signs_lib_uni<page>.png"`*

------------------------------
## 💻 Requirements

* Python 3.x
* Required external library: **Pillow (PIL)**
  *※If not installed, please run `pip install Pillow` before executing the scripts.*

------------------------------
## 📄 License

This mod is released under the MIT License. Please see the LICENSE file for details.

**AI Generation**: This package contains assets or source code generated by AI.
