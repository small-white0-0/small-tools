import math
import os
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

class Const:
    processed_suffix = ".CROPPED"

class WH:
    def __init__(self, width: int, height: int):
        g = math.gcd(width, height)
        self.w = int(width / g)
        self.h = int(height / g)

    def eq(self, other) -> bool:
        return self.w * other.h == self.h * other.w

def get_wh(model) -> WH:
    return WH(model.width, model.height)


def crop(picture: Image.Image, y1, y2):
    width = picture.width
    if y1 < 0:
        y1 = 0
    if y2 > picture.height:
        y2 = picture.height
    return picture.crop((0, y1, width, y2))


def split(picture: Image.Image, wh: WH, p: int = 0,max:int = 32,start:int|None = None):
    
    # 参数处理
    if start is None:
        start = 0

    if WH(picture.width, picture.height).eq(wh):
        return ([],None)
    h = picture.width * wh.h / wh.w
    h = int(h)
    diff = int(h * p / 100)
    result = []
    count = 0
    while start < picture.height:
        # 达到上限，提前结束，记录下一次开始位置
        if count < max:
            count += 1
        else:
            return (result,start)
        
        if start + h < picture.height:
            result.append(crop(picture, start, start + h))
        else:
            result.append(crop(picture, picture.height - h, picture.height))
        start += h - diff
    return (result,None)

def get_order(i:int):
    i = str(i)
    l = 3
    return "0"*(l - len(i)) + i

def process_picuture_arr(sub_pictures,file_path,suffix,s:int = 0):
    if len(sub_pictures) <= 1:
        return
    print("==>保存分割结果："+file_path)
    processed_suffix = Const().processed_suffix + suffix
    for sub in sub_pictures:
        s += 1
        new_file_path = file_path[:-len(suffix)] + "." + get_order(s) + processed_suffix
        sub.save(new_file_path, quality=95)
        print("写入"+new_file_path +"完成。")

def split_all(std: WH, dir: str, suffix=".png", p: int = 0,max:int = 32,recursive:bool = False):
    if max < 2:
        print("最小分割数目小于2，自动取2")
        max = 2
    processed_suffix = Const().processed_suffix + suffix
    files = os.listdir(dir)
    next_start = None
    for file in files:
        file_path = os.path.join(dir, file)
        index = 0
        if os.path.isdir(file_path) and recursive:
            split_all(std,file_path,suffix,p,max,recursive)
            continue
        if os.path.isfile(file_path) and file.endswith(suffix) and not file.endswith(processed_suffix):
            picture = Image.open(file_path)
            (sub_pictures,next_start) = split(picture, std, p,max,next_start)
            process_picuture_arr(sub_pictures,file_path,suffix)
            index += len(sub_pictures)
            # 循环处理超出限制部分
            while not next_start is None:
                (sub_pictures,next_start) = split(picture, std, p,max,next_start)
                process_picuture_arr(sub_pictures,file_path,suffix,index)
                index += len(sub_pictures)


def usage():
    msg = "\t标准格式模板的短图片 待处理图片所在的一级目录 [切分保留的百分比（默认为0）] [图片后缀（默认为'.png'] [一次性切分最大数目(默认32,不能小于2)] [是否递归处理（默认0）]"
    if len(sys.argv) > 0:
        print(os.path.basename(sys.argv[0]) + msg)
    else:
        print("xxxx.exe "+msg)


def main():
    if len(sys.argv) <= 1 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        usage()
    elif len(sys.argv) < 3 or len(sys.argv) > 7:
        print("参数数量错误")
        usage()
    else:
        std_path = sys.argv[1]
        dare_path = sys.argv[2]
        p = 0
        suffix = ".png"
        max = 32
        recursive = False
        if len(sys.argv) >= 4:
            p = int(sys.argv[3])
        if len(sys.argv) >= 5:
            suffix = sys.argv[4]
        if len(sys.argv) >= 6:
            max = int(sys.argv[5])
        if len(sys.argv) >= 7:
            recursive = True
        split_all(get_wh(Image.open(std_path)),
                  dare_path,
                  suffix,
                  p,
                  max,
                  recursive)

main()
