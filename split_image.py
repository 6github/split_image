import shutil 
import os
from PIL import Image, ImageChops

def make_temp_dir(input_path, temp_path):
    # 「temp_path\コード名\inputのフォルダ」のフォルダを作成する
    # inputのフォルダと同名のファイルが在れば、フォルダごと削除して作成しなおす
    # 作成したtempフォルダのパスを返す

    # 末尾のセパレートを削除
    input_path = input_path.rstrip(os.path.sep)

    # tempフォルダ下にスプリクトファイル名を作成
    code_name = os.path.basename(__file__)
    temp_dir = os.path.basename(input_path)
    paths = [code_name, temp_dir]

    for path in paths:
        temp_path = os.path.join(temp_path, path)

        try:
            os.mkdir(temp_path)
        except FileExistsError:
            if path == temp_dir:
                shutil.rmtree(temp_path)
                os.mkdir(temp_path)

    return temp_path 

def split_images(input_path, temp_path, include_subfolders=False):
    # include_subfoldersにTrueを指定するとサブフォルダも対象になります

    image_files = []
    
    # 入力フォルダ内の画像ファイルのリストを作成
    for root, _, files in os.walk(input_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, file))
        
        if not include_subfolders:
            break
    files_count = len(image_files)
    
    # 画像ファイルをタイムスタンプの昇順でソート
    image_files.sort(key=lambda file: os.path.getmtime(file))

    # 画像ファイルを順番に分割して保存
    for index, image_path in enumerate(image_files):
        if two_pages(image_path):
            crop_center_width_half(image_path, temp_path, index, files_count)
        else:
            split_image(image_path, temp_path, index, files_count)

def two_pages(image_path):
    # cropの左上のx座標が元座標の1/4以上だとTrue, 1/4以下だとFalseを返す
    source_img_width, _ = Image.open(image_path).size
    crop_x, _ = crop_size(image_path)
    return True if crop_x >= source_img_width // 4 else False

def crop_size(image_path):
# cropレンジを返します

    source_img = Image.open(image_path)

    # 閾値を設定して2値化を行う
    # 元の画像をグレースケールに変換する
    gr_scale_img = source_img.convert('L')

    # ビット演算を行い2値化する
    bw_img = gr_scale_img.point(lambda x: 0 if x < 68 else 255)

    # 2値化された画像の座標(0,0)の色を調べる
    col = bw_img.getpixel((0,0))

    # 2値化された座標(0,0)の色が黒(0)の場合は画像を白黒反転しない
    if col:
        bw_img = ImageChops.invert(bw_img)
    else:
        bw_img = bw_img

    # 画素がゼロでない(黒でない)領域のボックスを計算する
    x0, y0, x1, y1 = bw_img.convert('RGB').getbbox()
    # print(f'【Crop Range】{x0, y0, x1, y1}')
    return x0, y0

def crop_center_width_half(image_path, temp_path, index, files_count):
    # 横サイズの半分で中央部分を抽出したPILイメージを返す
    # 中央部に１ページしかない画像に使用するといい感じに抜き出せる

    original_image = Image.open(image_path)
    width, height = original_image.size
    
    # 画像の幅の半分を計算
    half_width = width // 2
    quarter_width = width // 4
    
    # 切り抜き範囲を計算
    left = quarter_width
    right = quarter_width + half_width 
    
    # 画像の中心部分を切り抜いて返す
    cropped_image = original_image.crop((left, 0, right, height))
    
    # 総ファイル数から桁数を求める
    digit_count = len(str(files_count))

    # inputファイルからフォルダ名を求める
    # path_name = input_dir.rstrip(os.path.sep)
    # dir_path, folder_name = os.path.split(path_name)

    dir_name = os.path.basename(temp_path)

    index = index * 2 + 1
    filename = os.path.join(temp_path, f"{dir_name}_{index:0{digit_count}d}.png")
    
    # 画像を保存
    cropped_image.save(filename)
    print(f'center {filename}')

def split_image(image_path, temp_path, index, files_count):
    original_image = Image.open(image_path)
    width, height = original_image.size
    half_width = width // 2
    
    # 画像を横半分に分割
    left_half = original_image.crop((0, 0, half_width, height))
    right_half = original_image.crop((half_width, 0, width, height))
    
    # Left側の番号を計算
    index_left = index * 2
    
    # Right側の番号を計算
    index_right = index * 2 + 1
    
    # 保存ファイル名の生成
    # 総ファイル数から桁数を求める
    digit_count = len(str(files_count))

    # inputファイルからフォルダ名を求める
    # path_name = input_dir.rstrip(os.path.sep)
    # dir_path, folder_name = os.path.split(path_name)

    dir_name = os.path.basename(temp_path)

    left_filename = os.path.join(temp_path, f"{dir_name}_{index_left:0{digit_count}d}.png")
    right_filename = os.path.join(temp_path, f"{dir_name}_{index_right:0{digit_count}d}.png")
    
    # 画像を保存
    left_half.save(left_filename)
    right_half.save(right_filename)

    print(f'left {left_filename}')
    print(f'right {right_filename}')

def archive_zip(input_path, temp_path):
    # ディレクトリ名の取得
    zip_filename = os.path.basename(input_path)
    temp_path_root = os.path.dirname(temp_path)
     
    shutil.make_archive(input_path, 'zip', root_dir=temp_path_root, base_dir=zip_filename)

def main(input_path, include_subfolders=False):
    temp_path = r'D:\temp'
    temp_path = make_temp_dir(input_path, temp_path)
    print(input_path, temp_path)
    split_images(input_path, temp_path, include_subfolders)
    archive_zip(input_path, temp_path)





import os
import shutil
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

from PIL import Image, ImageChops

def split_images(input_path, temp_path, include_subfolders=False):
    # 以前のsplit_images関数のコードをここに入れる
    # include_subfoldersにTrueを指定するとサブフォルダも対象になります

    image_files = []
    
    # 入力フォルダ内の画像ファイルのリストを作成
    for root, _, files in os.walk(input_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, file))
        
        if not include_subfolders:
            break
    files_count = len(image_files)
    
    # 画像ファイルをタイムスタンプの昇順でソート
    image_files.sort(key=lambda file: os.path.getmtime(file))

    # 画像ファイルを順番に分割して保存
    for index, image_path in enumerate(image_files):
        if two_pages(image_path):
            crop_center_width_half(image_path, temp_path, index, files_count)
        else:
            split_image(image_path, temp_path, index, files_count)

def two_pages(image_path):
    # cropの左上のx座標が元座標の1/4以上だとTrue, 1/4以下だとFalseを返す
    source_img_width, _ = Image.open(image_path).size
    crop_x, _ = crop_size(image_path)
    return True if crop_x >= source_img_width // 4 else False



def archive_zip(input_path, temp_path):
    # 以前のarchive_zip関数のコードをここに入れる
    # ...
    zip_filename = os.path.basename(input_path)
    temp_path_root = os.path.dirname(temp_path)
     
    shutil.make_archive(input_path, 'zip', root_dir=temp_path_root, base_dir=zip_filename)



def main(input_folder, output_folder, include_subfolders=False):
    split_images(input_folder, output_folder, include_subfolders)
    archive_zip(input_folder, output_folder)

def run_split_and_archive():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    main(input_folder, output_folder, include_subfolders=True)

def on_drop(event):
    folder_path = event.data
    input_folder_var.set(folder_path)

root = TkinterDnD.Tk()
root.title("Image Split and Archive")

# 入力フォルダ選択部分
input_folder_label = tk.Label(root, text="Input Folder:")
input_folder_label.pack()

input_folder_var = tk.StringVar()
input_folder_entry = tk.Entry(root, textvariable=input_folder_var)
input_folder_entry.pack()

# 出力フォルダ選択部分
output_folder_label = tk.Label(root, text="Output Folder:")
output_folder_label.pack()

output_folder_var = tk.StringVar()
output_folder_entry = tk.Entry(root, textvariable=output_folder_var)
output_folder_entry.pack()

# ドロップ＆ドラッグでフォルダを指定するためのラベル
drop_label = tk.Label(root, text="Drop & Drop a folder here:", font=("Helvetica", 12), relief="solid", width=30, height=5)
drop_label.pack()

# ドロップイベントの設定
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', on_drop)

# 実行ボタン
run_button = tk.Button(root, text="Run", command=run_split_and_archive)
run_button.pack()

root.mainloop()


if __name__ == "__main__":
    # input_dir = r"E:\Downloads\Figmaのきほん" # 入力元のフォルダ
    # input_path = r"D:\temp\manual\input_folder\Figmaのきほん"
    input_path = r'E:\Downloads\Figmaのきほん'

    main(input_path, include_subfolders=True)
    # archive_zip(input_dir, temp_dir)
