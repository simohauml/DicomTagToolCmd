"""Anonymize DICOM files from dicombase
"""
import argparse
import json
import os

import pydicom
from dicomanonymizer import anonymize, keep, empty, simpledicomanonymizer
# from dicomanonymizer.dicom_anonymization_databases.dicomfields_2023 import \
#     ALL_TAGS

import helper
import rules

TAGS_TO_KEEP = [
    (0x0008, 0x0020), # Study Date
    (0x0008, 0x0021), # Series Date
    (0x0008, 0x0022), # Acquisition Date
    (0x0008, 0x0023), # Content Date
    (0x0008, 0x002a), # Acquisition DateTime
    (0x0008, 0x0030), # Study Time
    (0x0008, 0x0031), # Series Time
    (0x0008, 0x0032), # Acquisition Time
    (0x0008, 0x0033), # Content Time
    (0x0008, 0x103e), # Series Description
    (0x0008, 0x0070), # Manufacturer
    (0x0008, 0x0080), # Institution Name
    (0x0008, 0x1090), # Manufacturer's Model Name
    (0x0010, 0x1030), # Patient's Weight
]

# TAGS_TO_EMPTY = [
#     (0x0008, 0x0070), # Manufacturer
#     (0x0008, 0x0080), # Institution Name
#     (0x0008, 0x1090), # Manufacturer's Model Name
# ]

TAGS_TO_EMPTY = []

ID_MAPPINGS = {}
PID_PREFIX = "A_"
DUMMY_NAME = "Anonymous Joe"

def main():
    """main function for anonymizing dicom files
    """
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--input",
        help="Path to the input dicom file or input directory which contains dicom files",
    )
    parser.add_argument(
        "--output",
        help="Path to the output dicom file or output directory which will contains dicom files",
    )
    args = parser.parse_args()

    input_root_path = args.input
    output_dicom_path = args.output

    extra_anonymization_rules = {}

    # ALL_TAGS variable is defined on file dicomfields.py
    # the 'keep' method is already defined into the dicom-anonymizer
    # It will overrides the default behaviour
    # for i in ALL_TAGS:
    #     extra_anonymization_rules[i] = keep
    for i in TAGS_TO_KEEP:
        extra_anonymization_rules[i] = keep

    for i in TAGS_TO_EMPTY:
        extra_anonymization_rules[i] = empty

    # extra_anonymization_rules[(0x0010, 0x0030)] = (
    #     set_date_to_year  # Patient's Birth Date
    # )

    func_replace_name = rules.replace_name(DUMMY_NAME)
    extra_anonymization_rules[(0x0010,0x0010)] = (
        func_replace_name # Patient's Name
    )

    dicom_paths = helper.find_dirs_with_files(input_root_path)
    tmp_dict = simpledicomanonymizer.dictionary.copy()

    for dicom_path in dicom_paths:
        files = os.listdir(dicom_path)
        for file in files:
            file_full_path = dicom_path + "/" + file
            dataset = pydicom.dcmread(file_full_path)
            pid = dataset.get((0x0010, 0x0020)).value
            if pid not in ID_MAPPINGS:
                ID_MAPPINGS[pid] = PID_PREFIX + helper.generate_guid(pid, 8)

        func_replace_id = rules.replace_patientid(ID_MAPPINGS)

        extra_anonymization_rules[(0x0010, 0x0020)] = (
            func_replace_id
        )
        simpledicomanonymizer.dictionary.update(tmp_dict)

        result_path = dicom_path.replace(input_root_path, output_dicom_path)
        if not os.path.exists(result_path):
            os.makedirs(result_path)
        # Launch the anonymization
        anonymize(
            dicom_path,
            result_path,
            extra_anonymization_rules,
            delete_private_tags=False,
        )
        tmp_dict = simpledicomanonymizer.dictionary.copy()

    with open("patient_mappings.txt", "w", encoding="utf-8") as f_w:
        f_w.write(json.dumps(ID_MAPPINGS))


if __name__ == "__main__":
    main()
