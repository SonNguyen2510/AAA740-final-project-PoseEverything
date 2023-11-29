import os
import json
import shutil

def copy_files_to_new_folder(json_folder, source_folder, destination_folder, folder_name_option=None, json_orginal_path=None):
    print(folder_name_option)
    id_list = []
    for json_file in os.listdir(json_folder):
        if json_file.endswith('.json'):
            json_file_path = os.path.join(json_folder, json_file)
            # print(json_file_path)
            
            with open(json_file_path, 'r') as f:
                data = json.load(f)

            for image_info in data['images']:
                file_name = image_info['file_name']
                image_id = image_info['id']
                bbox = None
                for annotation in data['annotations']:
                    if image_id != annotation['image_id']:
                        continue
                    bbox = annotation["bbox"]
                    break
                # Extract folder name from file_name
                folder_name = os.path.dirname(file_name)
                new_folder_path = os.path.join(destination_folder, folder_name)

                # Check if folder_name_option is provided and the file begins with it
                if folder_name_option and not file_name.startswith(folder_name_option):
                    # print(f"Image {image_id}: Skipped {file_name} - Folder name doesn't match")
                    continue
                if image_id not in id_list:
                    id_list.append(image_id)
                else:
                    continue

                # Extract file name without path
                file_name_only = os.path.basename(file_name)
                # (print(file_name_only.split('.')[0][-7:]))
                object_id_name = file_name_only.split('.')[0][-7:]

                # Search for the file in the source folder and its subfolders
                source_file_path = find_gt_in_subfolders(json_orginal_path, object_id_name, bbox)
                source_file_path = os.path.join(source_folder, source_file_path)

                if source_file_path and os.path.exists(source_file_path):
                    # Create a new folder only if the image is found
                    os.makedirs(new_folder_path, exist_ok=True)

                    destination_file_path = os.path.join(new_folder_path, file_name_only)
                    shutil.copyfile(source_file_path, destination_file_path)
                    # print(f"Image {image_id}: Copied {file_name} to {new_folder_path}")
                    print(f"Done!")
                else:
                    print(f"Image {image_id}: File {file_name} not found in {source_file_path} or its subfolders")

def calculate_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # Calculate the coordinates of the intersection rectangle
    x_intersection = max(x1, x2)
    y_intersection = max(y1, y2)
    w_intersection = min(x1 + w1, x2 + w2) - x_intersection
    h_intersection = min(y1 + h1, y2 + h2) - y_intersection

    # Check for non-overlapping boxes
    if w_intersection <= 0 or h_intersection <= 0:
        return 0.0

    # Calculate the area of the intersection rectangle
    intersection_area = w_intersection * h_intersection

    # Calculate the area of both bounding boxes
    area_box1 = w1 * h1
    area_box2 = w2 * h2

    # Calculate the union area
    union_area = area_box1 + area_box2 - intersection_area

    # Calculate IoU
    iou = intersection_area / union_area

    return iou


def find_gt_in_subfolders(json_path, file_name, bbox_compare):
    with open(json_path, 'r') as f:
        gt = json.load(f)
        best_iou = 0
        image_path = None
        for anotation in gt['annotations']:
            if file_name not in str(anotation['image_id']):
                continue
            bbox = anotation['bbox']
            iou = calculate_iou(bbox_compare, bbox)
            if best_iou < iou:
                best_iou = iou
                for image in gt['images']:
                    if anotation['image_id'] != image['id']:
                        continue
                    else:
                        image_path = image['file_name']
    print("IoU:   ",best_iou)
    return image_path
            
# Example usage:
json_folder = './'
source_folder = '/media/sonnguyen/DATA2/Study/superAI/data/car'
destination_folder = '/media/sonnguyen/DATA2/Study/superAI/Pose-for-Everything/tools/data/mp100'
folder_name_option = 'bus'  # Replace with the desired folder name or set to None
json_orginal_path = '/media/sonnguyen/DATA2/Study/superAI/data/car/carfusion_to_coco/car_keypoints.json'
folder_list = folder_name_option.split(', ')
for name in folder_list:
    copy_files_to_new_folder(json_folder, source_folder, destination_folder, name, json_orginal_path)
