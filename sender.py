"""Module for sending dicom files

"""
import logging
import sys
from pathlib import Path

from pydicom import dcmread
from pydicom.errors import InvalidDicomError
from pydicom.uid import ImplicitVRLittleEndian
from pynetdicom import AE, VerificationPresentationContexts  # debug_logger
from pynetdicom.sop_class import _STORAGE_CLASSES
from tqdm import tqdm

# pylint: disable=invalid-name

# config logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pacs_upload.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class PacsUploader:
    """Class for detecting dicom files and transfer
    """
    def __init__(self, pacs_config):
        """
        :param pacs_config: dictionary of PACS configuration
            {
                "ae_title": "YOUR_AE_TITLE",     # local AE Title
                "pacs_ae_title": "PACS_AE_TITLE",# remote AE Title
                "pacs_host": "192.168.1.100",    # PACS IP
                "pacs_port": 104,                 # PACS port
            }
        """
        self.config = pacs_config
        self.ae = AE(ae_title=self.config['ae_title'])
        # self.ae.add_requested_context('1.2.840.10008.5.1.4.1.1.7')  # 默认Secondary Capture
        self.ae.requested_contexts = VerificationPresentationContexts
        self.ae.add_requested_context(_STORAGE_CLASSES['CTImageStorage'],
                                      transfer_syntax=ImplicitVRLittleEndian)
        self.ae.add_requested_context(_STORAGE_CLASSES['PositronEmissionTomographyImageStorage'],
                                      transfer_syntax=ImplicitVRLittleEndian)

    def _connect_pacs(self):
        """create connection to PACS server"""
        try:
            assoc = self.ae.associate(
                self.config['pacs_host'],
                self.config['pacs_port']
            )
            if assoc.is_established:
                return assoc
            logging.error("can not create DICOM connection")
            return None
        except Exception as e:
            logging.error("connection error: %s", str(e))
            return None

    def _send_dicom(self, assoc, file_path):
        """send single DICOM file"""
        try:
            dataset = dcmread(file_path)

            # 自动添加所需传输语法, 目前出错，需要调查
            # ts = dataset.file_meta.TransferSyntaxUID
            # if ts not in self.ae.requested_contexts:
            #     self.ae.add_requested_context(ts)

            # send C-STORE request
            status = assoc.send_c_store(dataset)

            if status and status.Status in [0x0000, 0xB000]:
                logging.info("send successfully: %s", file_path)
                return True
            logging.error("send fail: %s (status code: %s)", file_path, hex(status.Status))
            return False
        except InvalidDicomError:
            logging.warning("ignore non-dicom file: %s", file_path)
            return False
        except Exception as e:
            logging.error("handle exception: %s: %s", file_path, str(e))
            return False

    def process_directory(self, root_dir):
        """process path recursively"""
        root_path = Path(root_dir)
        dicom_files = list(root_path.rglob('*.[dD][cC][mM]')) + \
                     list(root_path.rglob('*.[dD][iI][cC][oO][mM]'))

        total_files = len(dicom_files)
        success = 0
        failures = []

        logging.info("found %d DICOM files", total_files)

        with tqdm(total=total_files, desc="transfer progress") as pbar:
            assoc = self._connect_pacs()
            if not assoc:
                return

            try:
                for idx, file_path in enumerate(dicom_files, 1):
                    result = self._send_dicom(assoc, file_path)
                    if result:
                        success += 1
                    else:
                        failures.append(str(file_path))
                    pbar.update(1)

                    # 每100个文件重新连接防止超时
                    if idx % 100 == 0:
                        assoc.release()
                        assoc = self._connect_pacs()
                        if not assoc:
                            break
            finally:
                assoc.release()

        # generate report
        logging.info("\ntransfer done: %d/%d success", success, total_files)
        if failures:
            logging.warning("list of failed files: ")
            for f in failures:
                logging.warning(f)

if __name__ == "__main__":
    p_config = {
        "ae_title": "MY_CLIENT_AE",
        "pacs_ae_title": "PACS_AE",
        "pacs_host": "pacs.example.com",
        "pacs_port": 104,
        "timeout": 30
    }

    uploader = PacsUploader(p_config)
    uploader.process_directory("/path/to/dicom/root")
