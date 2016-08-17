import glob, os, fnmatch, uuid
import zipfile, re, hashlib
from input_files import ZAKUPKI_EXTRACT_DIR, ZAKUPKI_ZIP_DIR
from model_pckg.datamining import ProtocolJob, ConractJob
from loger_pack.logger import LoggerTrace
from loger_pack import PROTOCOL_LOG_FILE_OUT, CONTRACT_LOG_FILE_OUT
from xml_parsers.protocol_parser import ProtocolParser, ProtocolOkParser, ProtocolZKParser, ProtocolZPParser, ProtocolPOParser
from xml_parsers.contract_parser import ContractParser


class Zipper:
    def __init__(self, dir_path, worker):
        for root, dirs, files in os.walk(dir_path):
            for d in dirs:
                if d == worker:
                    self.zip_dir = os.path.join(root, d)
                    X_dir = self.zip_dir.split(os.sep)
                    for index, val in enumerate(X_dir):
                        if X_dir[index] == 'fcs_regions':
                            X_dir = X_dir[index + 1:]
                            break

                    self.pth = os.path.join(ZAKUPKI_EXTRACT_DIR, os.sep.join(X_dir))
                    print(self.pth)
                    if not os.path.exists(self.pth):
                        os.makedirs(self.pth)
                    if worker == 'protocols':
                        self.unzip_protocols_files()
                    elif worker == 'contracts':
                        self.unzip_conrtacts_files()


    @classmethod
    def md5sum(cls, filename, blocksize=65536):
        hash = hashlib.md5()
        with open(filename, "rb") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                hash.update(block)
        return hash.hexdigest()

    def insert_loading_log(self, zip_file, job):
        try:
            record = job.select().where(job.zip_id == uuid.UUID(self.md5sum(zip_file))).get()
            if record.status in ['success', 'skipped']:
                return None
            else:
                return record
        except job.DoesNotExist:
            return job.create(zip_id=uuid.UUID(self.md5sum(zip_file)), zip_name=zip_file.split(os.sep)[-1:][0], status='parsing')

    def unzip_protocols_files(self):
        zips = []
        for root, dirnames, filenames in os.walk(self.zip_dir):
            zips = [(os.path.join(root, filename)) for filename in fnmatch.filter(filenames, '*.zip')]
        for zip_name in sorted(zips, key=lambda x: os.path.getmtime(x)):
            zip_record = self.insert_loading_log(zip_name, ProtocolJob)
            if not zip_record:
                print("ZIP EXISTS")
                continue
            else:
                unziper = zipfile.ZipFile(zip_name)
                unziper.extractall(self.pth)
                unziper.close()
            for ext in ['fcsProtocolCancel_*.xml', 'fcsProtocolPO_*.xml', 'fcsProtocolZK*.xml','fcsProtocolP_*.xml', 'fcsProtocolOK*.xml',
                        'fcsProtocolPVK_*.xml', 'fcsProtocolPRO_*.xml',
                        'fcsProtocolPPO*.xml', 'fcsProtocolPRE_*.xml',
                        'fcsProtocolPR_*.xml','fcsProtocolPRZ_*.xml', 'fcsProtocolPP_*.xml', 'fcsProtocolPPI_*.xml',
                        'fcsProtocolPPN_*.xml', 'fcsProtocolEF[0-9]*.xml', 'fcsProtocolEFSingleApp*.xml',
                        'fcsProtocolEFSinglePart*.xml', 'fcsProtocolEFInvalidation*.xml',
                        'fcsProtocolZP*.xml', 'fcsProtocolEvasion_*.xml', 'fcsProtocolPOK_*.xml']:
                for xml_file in sorted(glob.glob(os.path.join(self.pth, ext))):
                    file_string = xml_file
                    print(xml_file)
                    logger_name = 'Run_protocol_loader' + xml_file
                    job_logger = LoggerTrace(logger_name, PROTOCOL_LOG_FILE_OUT, 'Protocol')
                    if ext in ['fcsProtocolOK*.xml', 'fcsProtocolPVK_*.xml', 'fcsProtocolPRO_*.xml', 'fcsProtocolPPO*.xml']:
                        parser = ProtocolOkParser(file_string)
                    elif ext == 'fcsProtocolPRE_*.xml':
                        parser = ProtocolParser(file_string)
                        parser = ProtocolOkParser(file_string)
                    elif ext in ['fcsProtocolZK*.xml','fcsProtocolP_*.xml']:
                        parser = ProtocolZKParser(file_string)
                    elif ext == 'fcsProtocolZP*.xml':
                        parser = ProtocolZPParser(file_string)
                    elif ext =='fcsProtocolPO_*.xml':
                        parser = ProtocolPOParser(file_string)
                    else:
                        parser = ProtocolParser(file_string)
                    os.remove(xml_file)
                    if parser.file_is_empty:
                        job_logger.write_warning('File is empty: %s' % xml_file)
                    else:
                        job_logger.write_log('File loaded: %s' % xml_file)
                    job_logger.close_log()
                    zip_record.status = 'success'
                    zip_record.save()

    def unzip_conrtacts_files(self):
        zips = []
        for root, dirnames, filenames in os.walk(self.zip_dir):
            zips = [(os.path.join(root, filename)) for filename in fnmatch.filter(filenames, '*.zip')]
        for zip_name in sorted(zips, key=lambda x: os.path.getmtime(x)):
            zip_record = self.insert_loading_log(zip_name, ConractJob)
            if not zip_record:
                print("ZIP EXISTS")
                continue
            else:
                if not zip_record:
                    print("ZIP EXISTS")
                    continue
                else:
                    unziper = zipfile.ZipFile(zip_name)
                    unziper.extractall(self.pth)
                    unziper.close()
                extensions = ['contract_*.xml', 'contractCancel_*.xml', 'contractProcedure_*.xml', 'contractProcedureCancel_*.xml']
                for ext in extensions:
                    for xml_file in sorted(glob.glob(os.path.join(self.pth, ext))):
                        file_string = xml_file
                        print(xml_file)
                        loger_name = 'Run_contract_loader' + xml_file
                        job_logger = LoggerTrace(loger_name, CONTRACT_LOG_FILE_OUT, 'Contract')
                        parser = ContractParser(file_string)
                        os.remove(xml_file)
                        job_logger.write_log('File loaded: %s' % (xml_file))
                        job_logger.close_log()
                        zip_record.status = 'success'
                        zip_record.save()

if __name__ == "__main__":
    run = Zipper(ZAKUPKI_ZIP_DIR, 'contracts')

