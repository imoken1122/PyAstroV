import cv2
import numpy as np
from PIL import Image
def get_keypoints(img, pt1=(0, 0), pt2=None):
    if pt2 is None:
        pt2 = (img.shape[1], img.shape[0])

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    mask = cv2.rectangle(np.zeros_like(gray), pt1, pt2, color=1, thickness=-1)
    akaze = cv2.AKAZE_create()

    return akaze.detectAndCompute(gray, mask=mask)

def get_matcher(img, kp2, des2):
    kp1, des1 = get_keypoints(img)

    if len(kp1) == 0 or len(kp2) == 0:
        return None

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    good = [m for m, n in matches if m.distance < 0.8 * n.distance]

    if len(good) == 0:
        return None

    target_position = [[kp1[m.queryIdx].pt[0], kp1[m.queryIdx].pt[1]] for m in good]
    base_position = [[kp2[m.trainIdx].pt[0], kp2[m.trainIdx].pt[1]] for m in good]

    apt1 = np.array(target_position)
    apt2 = np.array(base_position)
    return apt1, apt2

def get_alignment_img(img, kp2, des2):
    height, width = img.shape[:2]
    apt1, apt2 = get_matcher(img, kp2, des2)

    mtx = cv2.estimateAffinePartial2D(apt1, apt2)[0]

    if mtx is not None:
        return cv2.warpAffine(img, mtx, (width, height))
    else:
        return None
base = np.array(Image.open("img5.png"), dtype=np.uint8)[:,:,:3]
frame = np.array(Image.open("img4.png"), dtype=np.uint8)[:,:,:3]

kp, des = get_keypoints(base)
align = get_alignment_img(frame, kp, des)

Image.fromarray(align).save(fp="align.png", format = "png")

mask = align == 0
print(base.shape, frame.shape)
avg_image = cv2.addWeighted(base, 0.5, align, 0.5, 0)

avg_image[mask] = base[mask] 
Image.fromarray(avg_image).save("output.png", "png")

#ラプラシアンが低いほど画像がぼやけている
base = cv2.cvtColor(base, cv2.COLOR_RGB2GRAY)
frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
avg= cv2.cvtColor(avg_image, cv2.COLOR_RGB2GRAY)
l1 = cv2.Laplacian(base, cv2.CV_64F).var()
l2 = cv2.Laplacian(frame, cv2.CV_64F).var()
l3 = cv2.Laplacian(avg_image, cv2.CV_64F).var()
print(l1,l2,l3)
