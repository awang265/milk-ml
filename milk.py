#imports
from PIL import Image, ImageSequence
import os
import os.path
import glob
import re
import pandas as pd
import torch
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, utils

#Goal: read the file names into a list.
def read_filenames(filepath, ext=""):
    files = glob.glob(f'{filepath}*{ext}')
    tags = []
    for file in files:
        filename_ext = os.path.basename(file)
        tags.append(filename_ext)
    return tags, files

#Goal: convert TIFF images to PNG.
def tif2png(filepath):
    tags, files = read_filenames(filepath)
    os.mkdir(filepath + "/pngs")
    for file in files:
        filename_ext = os.path.basename(file)
        filename = os.path.splitext(filename_ext)[0]
        try:
            im = Image.open(file)
            for i, page in enumerate(ImageSequence.Iterator(im)):
                path = filepath + "/pngs/" + filename + ".png"        
                if not os.path.isfile(path):
                    try:
                        page.save(path)
                    except:
                        print(filename_ext)        
        except:
            print(filename_ext)

#Goal: classify the given manifest number to manifest class
def classify(mnfst_num):
        if re.search(r'^4{3}.{7}$', mnfst_num) != None:
            return "Foremost"
        elif re.search(r'^005.{7}$', mnfst_num) != None:
            return "DFA"
        elif re.search(r'^426.{3}$', mnfst_num) != None:
            return "Brewster"
        elif re.search(r'^0[78].{6}$', mnfst_num) != None:
            return "AMPI"
        elif re.search(r'^[23].{6}$', mnfst_num) != None:
            return "Scenic"
        elif re.search(r'^99.{8}$', mnfst_num) != None:
            return "LOL"
        elif re.search(r'^09.{6}$', mnfst_num) != None:
            return "NFO"
        else:
            return None
        
#Goal: prepare CSV file describing properties of each file
def create_csv(filepath, name='properties'):
    filename = []
    mnfst_num = []
    date = []
    rcv_site = []
    filename, files = read_filenames(filepath, ext='.png')
    for record in filename:
        fields = record.split(" - ")
        mnfst_num.append(re.findall(r'\d+', fields[0])[0])
        date.append(fields[4])
        rcv_site.append(fields[7])

    #classify based on mnfst_num
    mnfst_class = []
    for mnfst in mnfst_num:
        mnfst_class.append(classify(mnfst))
    data = {
    'Filename' : filename,
    'Manifest #' : mnfst_num,
    'Receipt Date' : date,
    'Receiving Site' : rcv_site,
    'Manifest Class' : mnfst_class
    }
    properties = pd.DataFrame(data)
    properties.to_csv(f'{filepath}{name}.csv', index=False)
    
#Goal: return Dataset of Manifest type.
class MilkDataset(Dataset):
    """Milk dataset."""

    def __init__(self, csv_file, root_dir, transform=None):
        """
        Arguments:
            csv_file (string): Path to the csv file with properties.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.tags_frame = pd.read_csv(csv_file, parse_dates=True, dtype={'Receiving Site' : 'object'})
        self.root_dir = root_dir
        self.transform = transform
    def __len__(self):
        return len(self.tags_frame)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        mnfst_name = os.path.join(self.root_dir,
                                self.tags_frame.iloc[idx, 0])
        mnfst = io.imread(mnfst_name)
        tags = self.tags_frame.iloc[idx, 1:]
        sample = {'manifest': mnfst, 'tags': tags}

        if self.transform:
            sample = self.transform(sample)

        return sample
    
#Given a folder of tif images, return a dataset
def buildDataset(filepath):
    try:
        tif2png(filepath)
    except:
        print('png directory exists')
    create_csv(f'{filepath}pngs/')
    
    return MilkDataset(csv_file=f'{filepath}/pngs/properties.csv', root_dir=f'{filepath}/pngs')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    