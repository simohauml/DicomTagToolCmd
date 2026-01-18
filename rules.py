""" DICOM Tag manipulate rules
"""

# Per https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html
# it is all right to retain only the year part of the birth date for
# de-identification purposes.
def set_date_to_year(dataset, tag):
    """Reformat date tag, just for testing

    Args:
        dataset (_type_): _description_
        tag (_type_): _description_
    """
    element = dataset.get(tag)
    if element is not None:
        element.value = f"{element.value[:4]}0101"  # YYYYMMDD format

def replace_name(newvalue: str):
    """Replace Patient Name with specific string

    Args:
        newvalue (str): new value
    """
    def apply_replace_name(dataset, tag):
        element = dataset.get(tag)
        if element is not None:
            element.value = newvalue
    return apply_replace_name

def replace_patientid(guid_dict: dict):
    """Replace patient id with specific one

    Args:
        guid_dict (dict): _description_
    Return:
        apply_replace_patientid: function
    """
    def apply_replace_patientid(dataset, tag):
        element = dataset.get(tag)
        if element is not None:
            temp = guid_dict[element.value]
            element.value = temp
    return apply_replace_patientid
