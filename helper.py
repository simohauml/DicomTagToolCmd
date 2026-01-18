"""Helper functions for DICOM anonymizer
"""
import os
import hashlib

def find_dirs_with_files(path):
    """Walk through path, list all subfolder with files
       Ignore empty folders and intermediate folder

    Args:
        path (_type_): root path

    Returns:
        list: list of paths
    """
    dirs_with_files = []
    # 遍历路径，root为当前目录，files为当前目录下的文件列表
    for root, _, files in os.walk(path):
        if files:  # 如果当前目录存在至少一个文件
            dirs_with_files.append(root)
    return dirs_with_files

def generate_guid(input_str: str, length: int = 32) -> str:
    """
    根据输入字符串生成指定长度的类GUID字符串

    :param input_str: 输入字符串
    :param length: 生成的GUID长度（1-128之间）
    :return: 生成的类GUID字符串
    """
    if not 1 <= length <= 128:
        raise ValueError("Length must be between 1 and 128")

    # 使用SHA-512生成128位十六进制字符串
    hash_obj = hashlib.sha512(input_str.encode('utf-8'))
    hex_digest = hash_obj.hexdigest()

    return hex_digest[:length]

def is_dicom(file_path):
    """
    :returns True if input file is a DICOM File. False otherwise.
    """
    try:
        with open(file_path, "rb") as tempfile:
            tempfile.seek(0x80, os.SEEK_SET)
            return tempfile.read(4) == b"DICM"
    except IOError:
        return False
