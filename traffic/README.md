PROJECT DEMONSTRATION: https://youtu.be/3hBztVN__UA

1st run layers:
Conv2d filters=32, kernel_size=(3, 3), activation="relu"
MaxPool2D pool_size=(2, 2), strides=2
Flatten
Dense units=128 activation="relu"
Dense units=43 activation="softmax"

COMPILATION: optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]

Thoughts: The model did perform well achieving 97.2% accuracy on a test set

2nd run - I added another Dense layer with 128 units and relu activation before the output layer and added Dropout(0.5) layers inbetween them

Thoughts: The model performed worse, achieving only 91% accuracy on a test set

3rd run - I decided to run the model for more epochs since maybe with such dropout the network has not enough runs to get the correct accuracy 

Thoughts: Even though the accuracy on the last epoch was 81% and the loss was about 0.6 the network performed significantly better achieving 96.2% accuracy on a test set

4th run - Removed one Dense and Dropout layer, decreased the dropout rate to 0.2

Thoughts: The network performed good on both training and evaluation achieving 97.6% (highest so far)

5th run - Increasing the number of epochs to 20

Thoughts: Increasing the number of epochs has improved the accuracy to almost 98%, I think I would rather stay with 10 epochs to lower computation time and avoid overfitting because the gain is not so significant

6th run - Added another Conv2d and MaxPool2D layer with the same params as layers in the 1st run

Thoughts: The accuracy on a test set has been increased to 98.4% so I will keep the change

7th run - Changed the strides parameter in both MaxPool layers to 1

Thoughts - The accuracy has improved to 99%, Probably the stride of 2 was too big and the network was losing too much information