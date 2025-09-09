import cv2
import numpy as np
import skimage.exposure
import matplotlib.pyplot as plt

img = cv2.imread('img/2.png', cv2.IMREAD_GRAYSCALE)
plt.imshow(img,cmap="grey")
plt.show()
img = cv2.imread('img/2.png')
hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(hsv_image)
plt.imshow(h)
plt.show()
plt.imshow(s)
plt.show()
plt.imshow(v)
plt.show()
s.fill(255)
v.fill(255)
hsv_image = cv2.merge([h, s, v])

plt.imshow(hsv_image)
plt.show()
img = cv2.GaussianBlur(img, (0,0), sigmaX=1.5, sigmaY=1.5)

Kx = np.array([[-1, 0, 1], 
               [-2, 0, 2], 
               [-1, 0, 1]])
Ky = np.array([[1,   2,  1], 
               [0,   0,  0], 
              [-1,  -2, -1]])

Ix = cv2.filter2D(img, -1, Kx)
Iy = cv2.filter2D(img, -1, Ky)

G = np.hypot(Ix, Iy)
G = skimage.exposure.rescale_intensity(G, in_range='image', out_range=(0,255)).astype(np.uint8)

theta = np.arctan2(Iy, Ix)
theta = skimage.exposure.rescale_intensity(theta, in_range='image', out_range=(0,255)).astype(np.uint8)
   
cv2.imwrite('black_dress_gradient_magnitude.png', G)
cv2.imwrite('black_dress_gradient_direction.png', theta)



plt.imshow( G)
plt.show()

plt.imshow(theta)
plt.show()