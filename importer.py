"""Import only DICOM files and reorgnize them
"""
import os
import shutil
import json

import pydicom
from tqdm import tqdm

import helper

DICT_IDENTIFIER = {}
DICT_STUDYID = {}

def main():
    """Import DICOM files
    """
    input_path = r"D:\playground\dicom\data3\NYCRM-070\trans"
    out_path = r"D:\playground\dicom\dicombase"

    dicom_paths = helper.find_dirs_with_files(input_path)

    with tqdm(total=len(dicom_paths), unit='path') as pbar:
        for path in dicom_paths:
            files = os.listdir(path)
            for file in files:
                file_full_path = path + "\\" + file
                if helper.is_dicom(file_full_path):
                    dataset = pydicom.read_file(file_full_path)
                    patientname = str(dataset.get((0x0010, 0x0010)).value)
                    patientid = dataset.get((0x0010, 0x0020)).value
                    p_identifier = patientid + "_" + patientname
                    studyid = dataset.get((0x0020, 0x000d)).value
                    seriesid = dataset.get((0x0020, 0x000E)).value
                    # if p_identifier not in DICT_IDENTIFIER:
                    #     DICT_IDENTIFIER[p_identifier] = helper.generate_guid(p_identifier)
                    # if studyid not in DICT_STUDYID:
                    #     DICT_STUDYID[studyid] = helper.generate_guid(studyid)
                    dicombase_path = out_path + "\\" + p_identifier + "\\" + studyid + "\\" + seriesid
                    if not os.path.exists(dicombase_path):
                        os.makedirs(dicombase_path)
                    newfilename = "anony_" + helper.generate_guid(file) + ".dcm"
                    dest_full_path = dicombase_path + "\\" + newfilename
                    shutil.copy(file_full_path, dest_full_path)
            pbar.update(1)

    # with open("dicombase_structure_identifier_mappings.txt", "w", encoding="utf-8") as f_w:
    #     f_w.write(json.dumps(DICT_IDENTIFIER))

    with open("dicombase_structure_studyid_mappings.txt", "w", encoding="utf-8") as f_w:
        f_w.write(json.dumps(DICT_STUDYID))

if __name__ == "__main__":
    main()
