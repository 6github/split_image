import os
from PIL import Image, ImageChops

def split_images(input_folder, output_folder, include_subfolders=False):
    image_files = []
    
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, file))
        
        if not include_subfolders:
            break
            
    files_count = len(image_files)
    
    image_files.sort(key=lambda file: os.path.getmtime(file))
    
    create_output_directory(input_folder, output_folder)
    
    for index, image_path in enumerate(image_files):
        if two_pages(image_path):
            crop_center_width_half(image_path, output_folder, index, files_count)
        else:
            split_image(image_path, output_folder, index, files_count)

def create_output_directory(input_folder, output_folder):
    path_name = os.path.basename(input_folder.rstrip(os.path.sep))
    output_folder = os.path.join(output_folder, path_name)
    
    try:
        os.makedirs(output_folder, exist_ok=True)
    except OSError:
        print("Error creating output directory")
        exit(1)

def two_pages(image_path):
    source_img_width, _ = Image.open(image_path).size
    crop_x, _ = crop_size(image_path)
    return crop_x >= source_img_width // 4

def crop_size(image_path):
    # cropレンジを返します
    source_img = Image.open(image_path)
    gr_scale_img = source_img.convert('L')
    bw_img = gr_scale_img.point(lambda x: 0 if x < 68 else 255)
    col = bw_img.getpixel((0, 0))

    if col:
        bw_img = ImageChops.invert(bw_img)

    x0, y0, _, _ = bw_img.convert('RGB').getbbox()
    return x0, y0

def crop_center_width_half(image_path, output_folder, index, files_count):
    original_image = Image.open(image_path)
    width, height = original_image.size
    half_width = width // 2
    quarter_width = width // 4
    left = quarter_width
    right = quarter_width + half_width 
    cropped_image = original_image.crop((left, 0, right, height))
    
    digit_count = len(str(files_count))
    path_name = os.path.basename(input_folder.rstrip(os.path.sep))
    index = index * 2 + 1
    filename = os.path.join(output_folder, f"{path_name}_{index:0{digit_count}d}.png")
    
    cropped_image.save(filename)
    print(f'center {filename}')

def split_image(image_path, output_folder, index, files_count):
    original_image = Image.open(image_path)
    width, height = original_image.size
    half_width = width // 2
    left_half = original_image.crop((0, 0, half_width, height))
    right_half = original_image.crop((half_width, 0, width, height))
    
    digit_count = len(str(files_count))
    path_name = os.path.basename(input_folder.rstrip(os.path.sep))
    index_left = index * 2
    index_right = index * 2 + 1
    
    left_filename = os.path.join(output_folder, f"{path_name}_{index_left:0{digit_count}d}.png")
    right_filename = os.path.join(output_folder, f"{path_name}_{index_right:0{digit_count}d}.png")
    
    left_half.save(left_filename)
    right_half.save(right_filename)
    print(f'left {left_filename}')
    print(f'right {right_filename}')

if __name__ == "__main__":
    input_folder = r"E:\Downloads\Figmaのきほん"
    output_folder = r"D:\temp\manual"
    split_images(input_folder, output_folder, include_subfolders=True)

