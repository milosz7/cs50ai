import cv2
import numpy as np
import os
import sys
import tensorflow as tf
import random

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4
IMG_CHANNELS = 3
ZOOM_IN_RATIO = 1.5
ZOOM_OUT_RATIO = 0.75
ZOOM_PROBA = 0.15


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []
    for i in range(NUM_CATEGORIES):
        subdir_path = os.path.join(data_dir, str(i))
        for img_name in os.listdir(subdir_path):
            img = cv2.imread(subdir_path + os.sep + img_name)
            img = img.astype("float64")
            img /= 255.0
            if random.random() < ZOOM_PROBA:
                img = zoom(img, ZOOM_IN_RATIO, ZOOM_IN_RATIO)
            elif random.random() < ZOOM_PROBA:
                img = zoom(img, ZOOM_OUT_RATIO, ZOOM_OUT_RATIO)
            
            img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT),
                     interpolation=cv2.INTER_AREA)
            images.append(img)
            labels.append(i)
    return (images, labels)


def zoom(img, fx, fy):
    return cv2.resize(img, None, fx=fx, fy=fy)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), input_shape=(
        IMG_WIDTH, IMG_HEIGHT, IMG_CHANNELS), activation="relu"))
    model.add(tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), input_shape=(
        IMG_WIDTH, IMG_HEIGHT, IMG_CHANNELS), activation="relu"))
    model.add(tf.keras.layers.MaxPool2D(pool_size=(2, 2), strides=1))
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(units=128, activation="relu"))
    model.add(tf.keras.layers.Dropout(rate=0.4))

    model.add(tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax"))
    model.compile(optimizer="adam",
                  loss="categorical_crossentropy", metrics=["accuracy"])
    return model


if __name__ == "__main__":
    main()
