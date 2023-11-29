import os
import json
import shutil

def copy_files_to_new_folder(json_folder, source_folder, destination_folder, folder_name_option=None):
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

                # Search for the file in the source folder and its subfolders
                source_file_path = find_file_in_subfolders(source_folder, file_name_only)


                if source_file_path and os.path.exists(source_file_path):
                    # Create a new folder only if the image is found
                    os.makedirs(new_folder_path, exist_ok=True)

                    destination_file_path = os.path.join(new_folder_path, file_name_only)
                    shutil.copyfile(source_file_path, destination_file_path)
                    # print(f"Image {image_id}: Copied {file_name} to {new_folder_path}")
                    print(f"Done!")
                else:
                    print(f"Image {image_id}: File {file_name} not found in {source_file_path} or its subfolders")

def find_file_in_subfolders(folder, file_name):
    for root, dirs, files in os.walk(folder):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

# Example usage:
json_folder = './'
source_folder = '/media/sonnguyen/DATA2/Study/superAI/data/OneHand10K/Train'
destination_folder = '/media/sonnguyen/DATA2/Study/superAI/Pose-for-Everything/tools/data/mp100'
folder_name_option = 'human_hand'  # Replace with the desired folder name or set to None
folder_list = folder_name_option.split(', ')
for name in folder_list:
    copy_files_to_new_folder(json_folder, source_folder, destination_folder, name)
