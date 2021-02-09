import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import pairwise_distances_argmin
from sklearn.datasets import load_sample_image
from sklearn.utils import shuffle
from time import time
from PIL import Image

n_colors = 32
dir_path = "./scaled"
out_path = "vectorized"

try:
  os.mkdir(out_path)
except:
  pass

dir = os.listdir(dir_path)
for i, filename in enumerate(dir):
  # Load the photo
  img = Image.open(f'{dir_path}/{filename}')
  img.load()
  img = np.asarray(img, dtype="uint8")

  # Convert to floats (need to be in the range [0-1])
  img = np.array(img, dtype=np.float64) / 255

  # Apply Gaussian Blur to get rid of some problematic noise
  # cv2.fastNlMeansDenoisingMulti(img, 2)
  # img = cv2.GaussianBlur(img, (3, 3), 2)

  # Load image and transform to a 2D numpy array.
  w, h, d = original_shape = tuple(img.shape)
  assert d == 3
  image_array = np.reshape(img, (w * h, d))

  print("Fitting model on a small sub-sample of the data")
  image_array_sample = shuffle(image_array, random_state=0)[:1000]
  kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(image_array_sample)
  # kmeans = MiniBatchKMeans(n_clusters=n_colors).fit(image_array_sample)

  # Get labels for all points
  print("Predicting color indices on the full image (k-means)")
  labels = kmeans.predict(image_array)

  codebook_random = shuffle(image_array, random_state=0)[:n_colors]
  print("Predicting color indices on the full image (random)")
  labels_random = pairwise_distances_argmin(codebook_random,
                                            image_array,
                                            axis=0)


  def recreate_image(codebook, labels, w, h):
      # Recreate the image from the code book & labels
      d = codebook.shape[1]
      image = np.zeros((w, h, d))
      label_idx = 0
      for i in range(w):
          for j in range(h):
              image[i][j] = codebook[labels[label_idx]]
              label_idx += 1
      return image
  
  # Make images
  image_kmeans = recreate_image(kmeans.cluster_centers_, labels, w, h)
  image_random = recreate_image(codebook_random, labels_random, w, h)
  
  # Save the images
  cv2.imwrite(f"{out_path}/{filename[:-4]}_{n_colors}_kmeans.png", cv2.cvtColor((image_kmeans*255).astype(np.uint8), cv2.COLOR_RGB2BGR))
  cv2.imwrite(f"{out_path}/{filename[:-4]}_{n_colors}_random.png", cv2.cvtColor((image_random*255).astype(np.uint8), cv2.COLOR_RGB2BGR))
  print(f'{i+1}/{len(dir)}: {filename[:-4]} vectorized')