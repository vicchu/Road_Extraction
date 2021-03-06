from datetime import datetime
from PIL import Image
import sys
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import time
import os
from skimage.color import rgb2gray
from skimage.feature import greycomatrix, greycoprops

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

t_total1 = time.time()
t1 = time.time()
print(str(datetime.now()) + ': initializing input data...')

rectSize = 5

image_name ="10978735_15"
# enter the image pass here
image_path = r'E:\Dataset\Validation\Valid-input\\'+image_name+'.TIFF'

inputImage = Image.open(image_path)

inputImageXSize, inputImageYSize = inputImage.size

outputImage = inputImage.crop(
    (rectSize // 2, rectSize // 2, inputImageXSize - (rectSize // 2), inputImageYSize - (rectSize // 2)))
outputImageXSize, outputImageYSize = outputImage.size

print(str(datetime.now()) + ': initializing model...')
featureColumns = [tf.contrib.layers.real_valued_column("", dimension=75)]

hiddenUnits = [100, 150, 100, 50]

classes = 3

classifier = tf.contrib.learn.DNNClassifier(feature_columns=featureColumns,
                                            hidden_units=hiddenUnits,
                                            n_classes=classes,
                                            model_dir='model')

t2 = time.time()
print("initializing model time :", (t2 - t1)/60)


def extractFeatures():
    features = np.zeros((((inputImageXSize - ((rectSize // 2) * 2)) * (inputImageYSize - ((rectSize // 2) * 2))),
                         rectSize * rectSize * 3), dtype=np.int)
    rowIndex = 0

    for x in range(rectSize // 2, inputImageXSize - (rectSize // 2)):
        for y in range(rectSize // 2, inputImageYSize - (rectSize // 2)):
            rect = (x - (rectSize // 2), y - (rectSize // 2), x + (rectSize // 2) + 1, y + (rectSize // 2) + 1)
            subImage = inputImage.crop(rect).load()


            colIndex = 0
            for i in range(rectSize):
                for j in range(rectSize):
                    features[rowIndex, colIndex] = subImage[i, j][0]
                    colIndex += 1
                    features[rowIndex, colIndex] = subImage[i, j][1]
                    colIndex += 1
                    features[rowIndex, colIndex] = subImage[i, j][2]
                    colIndex += 1
            rowIndex += 1

    return features


def constructOutputImage(predictions):
    outputImagePixels = outputImage.load()
    rowIndex = 0
    for x in range(outputImageXSize):
        for y in range(outputImageYSize):
            if predictions[rowIndex]==1:
                outputImagePixels[x, y] = (255, 0,0)
            elif predictions[rowIndex]==2:
                outputImagePixels[x, y] = (0, 255,0)
            else:
                outputImagePixels[x, y] = (0, 0, 0)

            rowIndex += 1


t1 = time.time()

print(str(datetime.now()) + ': processing image')
predictions = list(classifier.predict_classes(input_fn=extractFeatures))
t2 = time.time()
print("Extract features and predicting time :", (t2 - t1)/60)

t1 = time.time()
print(str(datetime.now()) + ': constructing output image...')
constructOutputImage(predictions)
t2 = time.time()


print(str(datetime.now()) + ': saving output image...')
outputImage.save('Results/'+image_name+'.png', 'JPEG')

print("constructing output image and ploting time : ", (t2 - t1)/60)
plt.figure()
plt.imshow(outputImage)
plt.show()

t_total2 = time.time()

print(str(datetime.now()) + ': Total time for predicting : ', (t_total2 - t_total1)/60)