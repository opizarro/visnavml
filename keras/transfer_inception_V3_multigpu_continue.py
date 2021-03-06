import os
import sys
import glob
import argparse
import matplotlib.pyplot as plt

import signal
from functools import partial

# python transfer_inception_V3.py
# --train_dir ~/data/training_data_collapsed/benthoz_299patch_split90-10/training/
#--val_dir ~/data/training_data_collapsed/benthoz_299patch_split90-10/validation/
# --plot

#python transfer_inception_V3_multigpu_continue.py --train_dir ~/data/training_data_balanced/benthoz_ziggy_299patch_split90-10/training/ --val_dir ~/data/training_data_balanced/benthoz_ziggy_299patch_split90-10/validation/ --input_model_file inceptionv3-MALC_9888.model --nb_epoch 20 --plot


# to parallelise model
# requieres training and validation set sizes to be divisible by n_gpu
extras = '/home/opizarro/git/keras-extras'
sys.path.append(extras)
from utils.multi_gpu import make_parallel
n_gpu = 2

from keras import __version__
from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import SGD
from keras.optimizers import Adam
from keras.optimizers import RMSprop

import tensorflow as tf
from keras.models import load_model


IM_WIDTH, IM_HEIGHT = 299, 299 #fixed size for InceptionV3
NB_EPOCHS = 10
BAT_SIZE = 32*n_gpu
FC_SIZE = 1024
NB_IV3_LAYERS_TO_FREEZE = 172


def get_nb_files(directory):
  """Get number of files by searching directory recursively"""
  if not os.path.exists(directory):
    return 0
  cnt = 0
  for r, dirs, files in os.walk(directory):
    for dr in dirs:
      cnt += len(glob.glob(os.path.join(r, dr + "/*")))
  return cnt


def setup_to_transfer_learn(model, base_model):
  """Freeze all layers and compile the model"""
  for layer in base_model.layers:
    layer.trainable = False
  model.compile(optimizer=Adam(lr=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
  #model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])

def add_new_last_layer(base_model, nb_classes):
  """Add last layer to the convnet
  Args:
    base_model: keras model excluding top
    nb_classes: # of classes
  Returns:
    new keras model with last layer
  """
  x = base_model.output
  x = GlobalAveragePooling2D()(x)
  x = Dense(FC_SIZE, activation='relu')(x) #new FC layer, random init
  predictions = Dense(nb_classes, activation='softmax')(x) #new softmax layer
  model = Model(inputs=base_model.input, outputs=predictions)
  return model


def setup_to_finetune(model):
  """Freeze the bottom NB_IV3_LAYERS and retrain the remaining top layers.
  note: NB_IV3_LAYERS corresponds to the top 2 inception blocks in the inceptionv3 arch
  Args:
    model: keras model
  """
  for layer in model.layers[:NB_IV3_LAYERS_TO_FREEZE]:
     layer.trainable = False
  for layer in model.layers[NB_IV3_LAYERS_TO_FREEZE:]:
     layer.trainable = True
  #print(model.summary())
  #model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy'])
  #model = make_parallel(model, n_gpu)
  #model.compile(optimizer=RMSprop(lr=0.00001), loss='categorical_crossentropy', metrics=['accuracy'])




def train(args):
  """Use transfer learning and fine-tuning to train a network on a new dataset"""
  nb_train_samples = get_nb_files(args.train_dir)
  nb_classes = len(glob.glob(args.train_dir + "/*"))
  nb_val_samples = get_nb_files(args.val_dir)
  nb_epoch = int(args.nb_epoch)
  batch_size = int(args.batch_size)





  # data prep
  train_datagen =  ImageDataGenerator(
      preprocessing_function=preprocess_input,
      #rotation_range=180,
      #width_shift_range=0.2,
      #height_shift_range=0.2,
      #shear_range=0.2,
      #fill_mode="reflect",
      #fill_mode="nearest",
      #zoom_range=0.2,
      vertical_flip=True,
      horizontal_flip=True
  )
  test_datagen = ImageDataGenerator(
      preprocessing_function=preprocess_input,
      #rotation_range=180,
      #width_shift_range=0.2,
      #height_shift_range=0.2,
      #shear_range=0.2,
      #fill_mode="reflect",
      #fill_mode="nearest",
      #zoom_range=0.2,
      vertical_flip=True,
      horizontal_flip=True
  )

  train_generator = train_datagen.flow_from_directory(
    args.train_dir,
    target_size=(IM_WIDTH, IM_HEIGHT),
    batch_size=batch_size,
  )

  validation_generator = test_datagen.flow_from_directory(
    args.val_dir,
    target_size=(IM_WIDTH, IM_HEIGHT),
    batch_size=batch_size,
  )

  # setup model
  model = load_model(args.input_model_file)
  # fine-tuning
  def signal_handler(signal, frame):
      print('You pressed Ctrl+C! Saving model as inceptionv3-forcedexit.model ')
      modelexit = model.get_layer('model_1')
      modelexit.save('inceptionv3-forcedexit.model')
      sys.exit(0)
  signal.signal(signal.SIGINT, signal_handler) # save model if ctrl+c
  #print(model.summary())
  #print("============> number of layers in model with multi-gpu %i") % len(model.layers)
  #  extract model from multi-gpu graph
  # model = model.get_layer('model_1')
  # print("============> number of layers in model without multi-gpu %i") % len(model.layers)
  # print('--------- Starting fine-tuning -------------------')
  setup_to_finetune(model)
  model = make_parallel(model, n_gpu)
  model.compile(optimizer=Adam(lr=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
  print(model.summary())
  history_ft = model.fit_generator(
    train_generator,
    #steps_per_epoch=50,
    steps_per_epoch=nb_train_samples // batch_size,
    epochs=nb_epoch,
    validation_data=validation_generator,
    #validation_steps=50,
    validation_steps=nb_val_samples // batch_size,
    #use_multiprocessing=True,
    #workers=4,
    class_weight='auto')
  model = model.get_layer('model_1')
  model.save(args.output_model_file)
  plot_training(history_ft)

def plot_training(history):
  acc = history.history['acc']
  val_acc = history.history['val_acc']
  loss = history.history['loss']
  val_loss = history.history['val_loss']
  epochs = range(len(acc))

  plt.figure()
  plt.plot(epochs, acc, 'r.')
  plt.plot(epochs, val_acc, 'r')
  plt.title('Training and validation accuracy')

  plt.figure()
  plt.plot(epochs, loss, 'r.')
  plt.plot(epochs, val_loss, 'r-')
  plt.title('Training and validation loss')
  plt.show()


if __name__=="__main__":
  a = argparse.ArgumentParser()
  a.add_argument("--train_dir")
  a.add_argument("--val_dir")
  a.add_argument("--nb_epoch", default=NB_EPOCHS)
  a.add_argument("--batch_size", default=BAT_SIZE)
  a.add_argument("--input_model_file")
  a.add_argument("--output_model_file", default="inceptionv3-ft.model")
  a.add_argument("--plot", action="store_true")

  args = a.parse_args()
  if args.train_dir is None or args.val_dir is None:
    a.print_help()
    sys.exit(1)

  if (not os.path.exists(args.train_dir)) or (not os.path.exists(args.val_dir)):
    print("directories do not exist")
    sys.exit(1)

train(args)
