import os
import lxml.etree as etree
from loger_pack.logger import LoggerDb
from loger_pack import RNP_LOG_FILE
from xml_parsers.parsing_tools import ParsingTools, Types
import datetime
from model_pckg.model import RegistryRnp, RegistryCustomers, Legals


class RnpPareser:
    def __init__(self, file):
        self.regnumber = None
        self.publishdate = None
        self.approvedate = None
        self.excludedate = None
        self.state = None
        self.createreason = None
        self.approvereason = None
        self.customer_regnum = None
        self.customer_inn = None
        self.customer_kpp = None
        self.customer_fullname = None
        self.supplier_inn = None
        self.supplier_kpp = None
        self.supplier_fullname = None
        self.supplier_type = None
        self.notification_num = None
        self.notification_lot = None
        self.contract_regnum = None
        self.rnp_dict = {
            'regnumber': {'path': './*/oos:registryNum', 'type': Types.string},
            'publishdate': {'path': './*/oos:publishDate', 'type': Types.date},
            'approvedate': {'path': './*/oos:approveDate', 'type': Types.date},
            'excludedate': {'path': './*/oos:exclude/oos:excludeDate', 'type': Types.date},
            'state': {'path': './*/oos:state', 'type': Types.string},
            'createreason': {'path': './*/oos:createReason', 'type': Types.string},
            'approvereason': {'path': './*/oos:approveReason', 'type': Types.string},
            'customer_regnum': {'path': './*/oos:customer/oos:regNum', 'type': Types.string},
            'customer_inn': {'path': './*/oos:customer/oos:INN', 'type': Types.string},
            'customer_kpp': {'path': './*/oos:customer/oos:KPP', 'type': Types.string},
            'customer_fullname': {'path': './*/oos:customer/oos:fullName', 'type': Types.string},
            'supplier_inn': {'path': './*/oos:unfairSupplier/oos:inn', 'type': Types.string},
            'supplier_kpp': {'path': './*/oos:unfairSupplier/oos:kpp', 'type': Types.string},
            'supplier_fullname': {'path': './*/oos:unfairSupplier/oos:fullName', 'type': Types.string},
            'supplier_type': {'path': './*/oos:unfairSupplier/oos:type', 'type': Types.string},
            'notification_num': {'path': './*/oos:purchase/oos:purchaseNumber', 'type': Types.string},
            'notification_lot': {'path': './*/oos:purchase/oos:lotNumber', 'type': Types.string},
            'contract_regnum': {'path': './*/oos:contract/oos:regNum', 'type': Types.string}
        }
        self.nsmp = {'oos': 'http://zakupki.gov.ru/oos/types/1', 'export': 'http://zakupki.gov.ru/oos/export/1',
                     'ns3': "http://zakupki.gov.ru/oos/printform/1"}
        self.file_is_empty = False
        self.file = file
        try:
            self.tree = etree.parse(file)
            self.filename = file.split(os.sep, -1)[-1:][0]
            self.get_nodes()
        except etree.XMLSyntaxError:
            self.file_is_empty = True
            print("File %s is empty!" % file)

    def get_nodes(self):
        self.root = self.tree.getroot()
        ParsingTools.get_values_from_xml(self, self.root, self.rnp_dict, nsmp=self.nsmp)
        self.customer_xpath = ParsingTools.get_xpath(self.tree, self.root, './*/oos:customer', self.nsmp)
        self.supplier_xpath = ParsingTools.get_xpath(self.tree, self.root, './*/oos:unfairSupplier', self.nsmp)
        self.notification_xpath = ParsingTools.get_xpath(self.tree, self.root, './*/oss:purchase', self.nsmp)
        print(self.regnumber)
        print(self.publishdate)
        self.put_data()

    def put_data(self):
        logname = 'RNP_loader' + self.filename
        print(self.filename)
        db_logger = LoggerDb(log_name=logname, log_file=RNP_LOG_FILE, job='RNP')
        customer = self.put_customer(self.customer_regnum, self.customer_inn, self.customer_kpp, self.customer_fullname,
                                     self.customer_xpath, self.filename, db_logger)
        supplier = self.put_supplier(self.supplier_inn, self.supplier_kpp, self.supplier_fullname, self.supplier_type,
                                     self.supplier_xpath, db_logger, self.filename)

        notification = self.put_notification(self.notification_num, self.notification_num, '44', self.notification_xpath,
                                             db_logger, self.filename)


    def put_customer(self, regnum, inn, kpp, fullname, xpath, filename, logger):
        inn = ParsingTools.check_inn(inn)
        customer_from_registry = RegistryCustomers.get_customer_data(regnum, '44')
        if customer_from_registry._legal:
            return customer_from_registry._legal
        else:
            if inn:
                return Legals.getLegaldata(inn, None, fullname, kpp, 'legal', xpath, logger, filename)
            else:
                return None

    def put_supplier(self, inn, kpp, fullname, supp_type,  xpath, logger, filename):
        inn = ParsingTools.check_inn(inn)
        if inn and len(inn) == 10:
            supplier = Legals.getLegaldata(inn, None,
                                           fullname,
                                           kpp, None,
                                           xpath, logger, filename)
        elif inn and len(inn) == 12:
                supplier = Legals.getLegaldata(inn, None,
                                               fullname, None,
                                               "individual",
                                               xpath, logger, filename)

        elif not inn and (supp_type == 'UF'):
            supplier = Legals.getLegaldata(None, None,
                                           fullname, None, "foreign",
                                           xpath, logger, self.filename)
        else:
            supplier = None
        return supplier


    def put_notification(self, regnum, lot, law, xpath, logger, filename):

if __name__ == '__main__':
    rnp = RnpPareser(r'C:\Test.Zakupki.local\fcs_fas\unfairSupplier_24120-15_24120.xml')
