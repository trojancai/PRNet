import numpy as np
import os
from glob import glob
import scipy.io as sio
from skimage.io import imread, imsave
from time import time

from api import PRN
from utils.write import write_obj
from utils.estimate_pose import estimate_pose
from utils.cv_plot import *

# ---- init PRN
os.environ['CUDA_VISIBLE_DEVICES'] = '0' # GPU number, -1 for CPU
prn = PRN(is_dlib = True, is_opencv = True) 


# ------------- load data
image_folder = 'TestImages/'
save_folder = 'TestImages/results/'
if not os.path.exists(save_folder):
    os.mkdir(save_folder)

types = ('*.jpg', '*.png')
image_path_list= []
for files in types:
    image_path_list.extend(glob(os.path.join(image_folder, files)))
total_num = len(image_path_list)

for i, image_path in enumerate(image_path_list):
    # read image
    image = imread(image_path)

    # the core: regress position map    
    pos = prn.process(image) # use dlib to detect face

    # -- Basic Applications
    # get landmarks
    kpt = prn.get_landmarks(pos)
    # 3D vertices
    vertices = prn.get_vertices(pos)
    # corresponding colors
    colors = prn.get_colors(image, vertices)

    # -- More
    # estimate pose
    camera_matrix, pose = estimate_pose(vertices)


    # ---------- Plot
    print vertices.shape
    image_pose = plot_pose_box(image, camera_matrix, kpt)
    cv2.imshow('sparse alignment', plot_kpt(image, kpt))
    cv2.imshow('dense alignment', plot_vertices(image, vertices))
    cv2.imshow('pose', plot_pose_box(image, camera_matrix, kpt))
    cv2.waitKey(0)


    # ---- Save
    name = image_path.strip().split('/')[-1][:-4]
    np.savetxt(os.path.join(save_folder, name + '_pose.txt'), pose) 
    np.savetxt(os.path.join(save_folder, name + '_kpt.txt'), kpt) 
    write_obj(os.path.join(save_folder, name + '.obj'), vertices, colors, prn.triangles) #save 3d face(can open with meshlab)
