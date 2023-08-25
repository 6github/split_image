import shutil 
import os
from PIL import Image, ImageChops
import pprint

def split_images(input_folder, output_folder, include_subfolders=False):
    # include_subfoldersにTrueを指定するとサブフォルダも対象になります

    image_files = []
    
    # 入力フォルダ内の画像ファイルのリストを作成
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, file))
        
        if not include_subfolders:
            break
    files_count = len(image_files)
    
    # 画像ファイルをタイムスタンプの昇順でソート
    image_files.sort(key=lambda file: os.path.getmtime(file))

    # inputフォルダと同名のフォルダをoutputフォルダ下に作成する
    path_name = input_folder.rstrip(os.path.sep)
    dir_path, folder_name = os.path.split(path_name)
    output_folder = os.path.join(output_folder, folder_name)
    try:
        os.mkdir(output_folder)
    except FileExistsError:
        pass
    
    # 画像ファイルを順番に分割して保存
    for index, image_path in enumerate(image_files):
        if two_pages(image_path):
            crop_center_width_half(image_path, output_folder, index, files_count)
        else:
            split_image(image_path, output_folder, index, files_count)

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

def crop_center_width_half(image_path, output_folder, index, files_count):
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
    path_name = input_folder.rstrip(os.path.sep)
    dir_path, folder_name = os.path.split(path_name)

    index = index * 2 + 1
    filename = os.path.join(output_folder, f"{folder_name}_{index:0{digit_count}d}.png")
    
    # 画像を保存
    cropped_image.save(filename)
    print(f'center {filename}')

def split_image(image_path, output_folder, index, files_count):
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
    path_name = input_folder.rstrip(os.path.sep)
    dir_path, folder_name = os.path.split(path_name)

    left_filename = os.path.join(output_folder, f"{folder_name}_{index_left:0{digit_count}d}.png")
    right_filename = os.path.join(output_folder, f"{folder_name}_{index_right:0{digit_count}d}.png")
    
    # 画像を保存
    left_half.save(left_filename)
    right_half.save(right_filename)

    print(f'left {left_filename}')
    print(f'right {right_filename}')



def archive_zip(input_folder, output_folder):
    # ディレクトリ名の取得
    zip_filename = os.path.basename(input_folder)
    zip_path = os.path.join(output_folder, zip_filename)

    print(f'【zip_filename】{zip_filename}')
    print(f'【zip_path】{zip_path}')
    print(f'【output_folder】{output_folder}')

    # shutil.make_archive(zip_path, 'zip', root_dir=zip_path, base_dir=zip_path)
    shutil.make_archive(zip_path, 'zip', root_dir=output_folder, base_dir=zip_filename)

def main(input_folder, output_folder, include_subfolders=False):
    split_images(input_folder, output_folder, include_subfolders)
    archive_zip(input_folder, output_folder)

if __name__ == "__main__":
    # input_folder = r"E:\Downloads\Figmaのきほん" # 入力元のフォルダ
    input_folder = r"D:\temp\manual\input_folder\Figmaのきほん"
    output_folder = r"D:\temp\manual"  # 出力フォルダのパス

    main(input_folder, output_folder, include_subfolders=True)
    # archive_zip(input_folder, output_folder)
