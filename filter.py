# Filter DICOM files based on specific criteria

import os

def filter_dicom_files(input_dir, output_dir, criteria_func):
    """Filter DICOM files from input_dir to output_dir based on criteria_func

    Args:
        input_dir (str): Path to the input directory containing DICOM files.
        output_dir (str): Path to the output directory to save filtered DICOM files.
        criteria_func (function): Function that takes a DICOM dataset and returns True if it meets criteria.
    """
    import pydicom
    import shutil

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                dataset = pydicom.dcmread(file_path)
                if criteria_func(dataset):
                    dest_path = os.path.join(output_dir, file)
                    shutil.copy(file_path, dest_path)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

def example_criteria(dataset):
    """Example criteria function that filters DICOM files by Patient's Age > 30

    Args:
        dataset (pydicom.Dataset): The DICOM dataset to evaluate.

    Returns:
        bool: True if the dataset meets the criteria, False otherwise.
    """
    age_tag = (0x0010, 0x1010)  # Patient's Age
    age_value = dataset.get(age_tag)
    if age_value:
        try:
            age = int(age_value.value[:-1])  # Remove the trailing 'Y' and convert to int
            return age > 30
        except ValueError:
            return False
    return False    

if __name__ == "__main__":
    input_directory = "path/to/input/dicom/files"
    output_directory = "path/to/output/filtered/dicom/files"
    filter_dicom_files(input_directory, output_directory, example_criteria) 
