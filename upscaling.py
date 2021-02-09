# -- NEEDED PACKAGES -- #
# opencv-python
# opencv-contrib-python

import cv2
from cv2 import dnn_superres

# Create an SR object
sr = dnn_superres.DnnSuperResImpl_create()

# Read image
image = cv2.imread('img11.png')

# Read the desired model
path = "LapSRN_x8.pb"
sr.readModel(path)

# Set the desired model and scale to get correct pre- and post-processing
sr.setModel("lapsrn", 8)

# Upscale the image
result = sr.upsample(image)

# Save the image
cv2.imwrite("./upscaled.png", result)