import cv2
import math
import sys
import torch
import numpy as np
import argparse
from imageio import mimsave
import pathlib

'''==========import from our code=========='''
sys.path.append('.')
import config as cfg
from Trainer import Model
from benchmark.utils.padder import InputPadder

parser = argparse.ArgumentParser()
parser.add_argument('--model', default='ours_t', type=str)
parser.add_argument('--n', default=16, type=int)
args = parser.parse_args()
assert args.model in ['ours_t', 'ours_small_t'], 'Model not exists!'


'''==========Model setting=========='''
TTA = True
if args.model == 'ours_small_t':
    TTA = False
    cfg.MODEL_CONFIG['LOGNAME'] = 'ours_small_t'
    cfg.MODEL_CONFIG['MODEL_ARCH'] = cfg.init_model_config(
        F = 16,
        depth = [2, 2, 2, 2, 2]
    )
else:
    cfg.MODEL_CONFIG['LOGNAME'] = 'ours_t'
    cfg.MODEL_CONFIG['MODEL_ARCH'] = cfg.init_model_config(
        F = 32,
        depth = [2, 2, 2, 4, 4]
    )
model = Model(-1)
model.load_model()
model.eval()
model.device()


# print(f'=========================Start Generating=========================')
# I0 = cv2.imread('example/img1.jpg')
# I2 = cv2.imread('example/img2.jpg') 
# I0_ = (torch.tensor(I0.transpose(2, 0, 1)).cuda() / 255.).unsqueeze(0)
# I2_ = (torch.tensor(I2.transpose(2, 0, 1)).cuda() / 255.).unsqueeze(0)
# padder = InputPadder(I0_.shape, divisor=32)
# I0_, I2_ = padder.pad(I0_, I2_)
# images = [I0[:, :, ::-1]]
# preds = model.multi_inference(I0_, I2_, TTA=TTA, time_list=[(i+1)*(1./args.n) for i in range(args.n - 1)], fast_TTA=TTA)
# for pred in preds:
#     images.append((padder.unpad(pred).detach().cpu().numpy().transpose(1, 2, 0) * 255.0).astype(np.uint8)[:, :, ::-1])
# images.append(I2[:, :, ::-1])
# 

global images
images =[]

def InterFrameLoop(image1, image2):
    global images
    print(f'===== Start Loop For {image1} and {image2} =====')
    I0 = cv2.imread(image1)
    I2 = cv2.imread(image2) 

    I0_ = (torch.tensor(I0.transpose(2, 0, 1)).cuda() / 255.).unsqueeze(0)
    I2_ = (torch.tensor(I2.transpose(2, 0, 1)).cuda() / 255.).unsqueeze(0)

    padder = InputPadder(I0_.shape, divisor=32)
    I0_, I2_ = padder.pad(I0_, I2_)

    images.append([I0[:, :, ::-1]])
    preds = model.multi_inference(I0_, I2_, TTA=TTA, time_list=[(i+1)*(1./args.n) for i in range(args.n - 1)], fast_TTA=TTA)
    for pred in preds:
        images.append((padder.unpad(pred).detach().cpu().numpy().transpose(1, 2, 0) * 255.0).astype(np.uint8)[:, :, ::-1])
    images.append(I2[:, :, ::-1])
    print(f'===== End Loop for {image1} and {image2}  =====')

print(f'=========================Start Generating=========================')

imagefiles =[f for f in pathlib.Path('./images/').iterdir() if f.is_file()]
imagefiles.sort()
for i in range(0, len(imagefiles)-1):
    InterFrameLoop( str(imagefiles[i].absolute()), str(imagefiles[i+1].absolute()))

mimsave('example/out_Nx.gif', images, fps=args.n)
print(f'=========================Done=========================')