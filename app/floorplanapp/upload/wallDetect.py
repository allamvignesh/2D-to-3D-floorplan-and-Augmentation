import os
import json
from django.conf import settings
import cv2
import numpy as np

def fetch(filename):
        print("[SERVER] Detecting Edges", os.path.join(settings.MEDIA_ROOT, filename))
        img = cv2.imread(os.path.join(settings.MEDIA_ROOT, filename))
        imgX = np.flip(img, axis=1)
        cv2.imwrite(os.path.join(settings.MEDIA_ROOT, filename), imgX)
        gray = cv2.cvtColor(imgX, cv2.COLOR_BGR2GRAY)

        # convert gray to binary image
        _, thresh = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )


        # noise removal
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(
                thresh,
                cv2.MORPH_OPEN,
                kernel,
                iterations=2,
        )

        # dilate image
        sure_bg = cv2.dilate(
                opening, kernel, iterations=3
        )

        # sharpen image
        dist_transform = cv2.distanceTransform(
                opening, cv2.DIST_L2, 5
        )

        # get ceter of walls
        ret, sure_fg = cv2.threshold(
                0.5 * dist_transform,
                0.2 * dist_transform.max(),
                255,
                0,
        )

        # remove center and keep only edges
        sure_fg = np.uint8(sure_fg)
        wall_img = cv2.subtract(sure_bg, sure_fg)


        # extract contours
        boxes = []
        contours, _ = cv2.findContours(
                wall_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # simplify outlines
        for cnt in contours:
                epsilon = 0.001 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                boxes.append(approx)

        # finding outer contour
        ret, thresh = cv2.threshold(
                gray,
                200,
                255,
                cv2.THRESH_BINARY_INV,
        )

        contours, hierarchy = cv2.findContours(
                thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # optimize the contour
        largest_contour_area = 0
        for cnt in contours:
                if cv2.contourArea(cnt) > largest_contour_area:
                        largest_contour_area = cv2.contourArea(cnt)
                        largest_contour = cnt

        epsilon = 0.001 * cv2.arcLength(largest_contour, True)
        contour = cv2.approxPolyDP(largest_contour, epsilon, True)


        def points_inside_contour(points, contour):
                for x, y in points:
                        if cv2.pointPolygonTest(contour, (int(x), int(y)), False) == 1.0:
                                return True
                return False

        res = []
        for wall in boxes:
                for point in wall:
                        if points_inside_contour(point, contour):
                                res.append(wall)
                                break
        boxes = res

        def scale_point_to_vector(boxes, height=0, scale=np.array([1, 1, 1])):
                res = []
                for box in boxes:
                        for pos in box:
                                res.extend([[(pos[0]) / 100, (pos[1]) / 100, height]])
                return res

        def create_4xn_verts_and_faces(boxes, height=1, scale=np.array([1, 1, 1])):
                counter = 0
                verts = []

                for box in boxes:
                        verts.extend([scale_point_to_vector(box, 1, scale)])
                        counter += 1

                faces = []

                for room in verts:
                        count = 0
                        temp = ()
                        for _ in room:
                                temp = temp + (count,)
                                count += 1
                        faces.append([(temp)])

                return verts, faces, counter

        print("[SERVER] Generating 3D model")
        verts, faces, _ = create_4xn_verts_and_faces(boxes=boxes)

        with open("scans/wall_horizontal_verts.txt", "w") as f:
                f.write(json.dumps(verts))

        with open("scans/wall_horizontal_faces.txt", "w") as f:
                f.write(json.dumps(faces))
        
        os.system("cd ..\\blender && blender -b -P ..\\floorplanapp\\upload\\3dfily.py")

        from skimage.metrics import structural_similarity as ssim

        kernel = np.ones((3, 3), np.uint8)  # Small kernel for noise removal
        processed = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)

        if thresh.shape != processed.shape:
                thresh = cv2.resize(thresh, (processed.shape[1], processed.shape[0]))

        edges = cv2.Canny(thresh, 100, 200)
        reference_edges = cv2.Canny(processed, 100, 200)

        matching_pixels = np.sum(edges == reference_edges)
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_accuracy = (matching_pixels / total_pixels) * 100

        ssim_score = ssim(edges, reference_edges) * 100

        print("\n")
        print(f"Wall Edge Accuracy: {edge_accuracy:.2f}%")
        print(f"SSIM Edge Similarity: {ssim_score:.2f}%")
        print("\n")