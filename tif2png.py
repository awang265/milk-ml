#Goal: convert TIFF images to PNG.
from PIL import Image, ImageSequence
import os
import os.path
import glob
def tif2png(filepath):
    files = glob.glob(f'{filepath}/*.tif')
    for file in files:
        filename_ext = os.path.basename(file)
        filename = os.path.splitext(filename_ext)[0]
        try:
            im = Image.open(file)
            for i, page in enumerate(ImageSequence.Iterator(im)):
                path = filepath + "/" + filename + ".png"        
                if not os.path.isfile(path):
                    try:
                        page.save(path)
                    except:
                        print(filename_ext)        
        except:
            print(filename_ext)