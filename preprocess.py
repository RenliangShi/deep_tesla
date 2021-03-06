import os
import cv2
import params
import numpy as np
import pandas as pd
import utils

img_height = params.img_height
img_width = params.img_width
img_channels = params.img_channels

data_dir = params.data_dir
out_dir = params.out_dir
model_dir = params.model_dir

def img_preprocess(img, color_mode='RGB', flip=True):
    """
    Processes the image and returns it
    :param img: The image to be processed
    :return: Returns the processed image
    """
    ## Chop off 1/3 from the top and cut bottom 150px(which contains the head of car)
    shape = img.shape
    ratio = img_height / img_width
    h1 = int(shape[0]/3)
    h2 = shape[0]-150
    w = (h2 - h1) / ratio
    padding = int(round((img.shape[1] - w) / 2))
    img = img[h1:h2, padding:-padding]
    ## Resize the image
    img = cv2.resize(img, (params.img_width, params.img_height), interpolation=cv2.INTER_AREA)
    if color_mode == 'YUV':
    	img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    if flip:
    	img = cv2.flip(img, 1)

    return img


def frame_count_func(file_path):
    '''return frame count of this video'''
    cap = cv2.VideoCapture(file_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    return frame_count


def load_test(color_mode='RGB'):
	imgs = []
	wheels = []
	epochs = [10]
	for epoch in epochs:
	    vid_path = utils.join_dir(params.data_dir, 'epoch{:0>2}_front.mp4'.format(epoch))

	    assert os.path.isfile(vid_path)
	    frame_count = frame_count_func(vid_path)
	    cap = cv2.VideoCapture(vid_path)
	    for frame_id in range(frame_count):
	    	while True:
	    		ret, img = cap.read()
	    		if not ret:
	    			break
	    		img = img_preprocess(img, color_mode, flip=False)
	    		imgs.append(img)

	    csv_path = os.path.join(data_dir, 'epoch{:0>2}_steering.csv'.format(epoch))
	    rows = pd.read_csv(csv_path)
	    yy = rows['wheel'].values

	    wheels.extend(yy)

	    cap.release()

	imgs = np.array(imgs)
	wheels = np.array(wheels)
	wheels = np.reshape(wheels,(len(wheels),1))


	return imgs, wheels


def load_train(color_mode='RGB', flip=True):
	imgs = []
	wheels = []
	epochs = [1, 2, 3, 4, 5, 6, 7, 8, 9]
	for epoch in epochs:
		vid_path = utils.join_dir(params.data_dir, 'epoch{:0>2}_front.mp4'.format(epoch))

		assert os.path.isfile(vid_path)
		frame_count = frame_count_func(vid_path)
		cap = cv2.VideoCapture(vid_path)
		for frame_id in range(frame_count):
			while True:
				ret, img = cap.read()
				if not ret:
					break
				img = img_preprocess(img, color_mode, flip)
				imgs.append(img)

		csv_path = os.path.join(data_dir, 'epoch{:0>2}_steering.csv'.format(epoch))
		rows = pd.read_csv(csv_path)
		yy = rows['wheel'].values
		if  flip:
			yy = yy * (-1.0)
		wheels.extend(yy)

		cap.release()

	imgs = np.array(imgs)
	wheels = np.array(wheels)
	wheels = np.reshape(wheels,(len(wheels),1))

	return imgs, wheels


# train_data_RGB
def train_data_RGB():
	imgs_RGB_with_flip, wheels_RGB_with_flip = load_train(color_mode='RGB', flip=True)
	imgs_RGB_without_flip, wheels_RGB_without_flip = load_train(color_mode='RGB', flip=False)
	return np.concatenate((imgs_RGB_with_flip, imgs_RGB_without_flip), axis=0), np.concatenate((wheels_RGB_with_flip, wheels_RGB_without_flip), axis=0)


# train_data_YUV
def train_data_YUV():
	imgs_YUV_with_flip, wheels_YUV_with_flip = load_train(color_mode='YUV', flip=True)
	imgs_YUV_without_flip, wheels_YUV_without_flip = load_train(color_mode='YUV', flip=False)
	return np.concatenate((imgs_YUV_with_flip, imgs_YUV_without_flip), axis=0), np.concatenate((wheels_YUV_with_flip, wheels_YUV_without_flip), axis=0)


# test_data_RGB
def test_data_RGB():
	return load_test(color_mode='RGB')


# test_data_YUV
def test_data_YUV():
	return load_test(color_mode='YUV')

