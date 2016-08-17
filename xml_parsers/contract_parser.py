import os
import lxml.etree as etree
from loger_pack.logger import LoggerDb
from loger_pack import CONTRACT_LOG_FILE
from xml_parsers.parsing_tools import ParsingTools
import datetime
from model_pckg.model import Contracts, Notifications, RegistryCustomers, Customers, Legals, ContractsProducts, Contacts


class ContractParser:
    def __init__(self, file):
        self.file_is_empty = False
        self.file = file
        try:
            self.tree = etree.parse(file)
            self.filename = file.split(os.sep, -1)[-1:][0]
            self.get_top_nodes()
        except etree.XMLSyntaxError:
            self.file_is_empty = True
            print("File %s is empty!" % file)

    def get_top_nodes(self):
        self.root = self.tree.getroot()
        self.nsmp = {'oos': 'http://zakupki.gov.ru/oos/types/1', 'export': 'http://zakupki.gov.ru/oos/export/1',
                     'ns3': "http://zakupki.gov.ru/oos/printform/1"}
        self.contract_xml_type = ParsingTools.get_node_name(self.root)  # Gets name of first child
        for child in self.root:
            if self.contract_xml_type == 'contractCancel':
                self.publishdate = ParsingTools.get_val_from_node(child.xpath("./oos:cancelDate",namespaces=self.nsmp),is_date=True)
            else:
                self.publishdate = ParsingTools.get_val_from_node(child.xpath("./oos:publishDate", namespaces=self.nsmp), is_date=True)
            self.schemaversion = child.attrib
            self.signdate = ParsingTools.get_val_from_node(child.xpath("./oos:signDate", namespaces=self.nsmp), is_date=True)
            if self.contract_xml_type == 'contract':
                enddate_month = ParsingTools.get_val_from_node(child.xpath("./oos:executionDate/oos:month",namespaces=self.nsmp))
                enddate_year = ParsingTools.get_val_from_node(child.xpath("./oos:executionDate/oos:year", namespaces=self.nsmp))
                self.enddate = ParsingTools.get_val_from_node(child.xpath("./oos:executionPeriod/oos:endDate", namespaces=self.nsmp), is_date=True)
                if not self.enddate:
                    self.enddate = datetime.date(year=int(enddate_year), month=int(enddate_month), day=1)
            elif self.contract_xml_type == 'contractProcedure':
                if int(self.schemaversion['schemeVersion'][0]) < 5:
                    enddate_month = ParsingTools.get_val_from_node(child.xpath("./oos:executions/oos:stage/oos:month",namespaces=self.nsmp))
                    enddate_year = ParsingTools.get_val_from_node(child.xpath("./oos:executions/oos:stage/oos:year",namespaces=self.nsmp))
                    if enddate_year:
                        self.enddate = datetime.date(year=int(enddate_year), month=int(enddate_month), day=1)
                    else:
                        self.enddate = None
                else:
                    enddate_month = ParsingTools.get_val_from_node(child.xpath("./oos:executions/oos:stage/oos:oldStage/oos:month", namespaces=self.nsmp))
                    enddate_year = ParsingTools.get_val_from_node(child.xpath("./oos:executions/oos:stage/oos:oldStage/oos:year", namespaces=self.nsmp))
                    self.enddate = ParsingTools.get_val_from_node(child.xpath("./oos:executions/oos:stage/oos:endDate", namespaces=self.nsmp), is_date=True)
                    if not self.enddate and enddate_year:
                        self.enddate = datetime.date(year=int(enddate_year), month=int(enddate_month), day=1)
            else:
                self.enddate = None
            self.regnumber = ParsingTools.get_val_from_node(child.xpath("./oos:regNum", namespaces=self.nsmp))
            if self.regnumber:
                self.regnumber_xpath = self.tree.getpath(child.xpath("./oos:regNum", namespaces=self.nsmp)[0])
            self.price = ParsingTools.get_val_from_node(child.xpath("./oos:price", namespaces=self.nsmp), is_num=True)
            self.currency = ParsingTools.get_val_from_node(child.xpath("./oos:currency/oos:code", namespaces=self.nsmp))
            self.price_rur = self.price
            if not self.price:
                self.price = ParsingTools.get_val_from_node(child.xpath("./oos:priceInfo/oos:price", namespaces=self.nsmp), is_num=True)
                self.currency = ParsingTools.get_val_from_node(child.xpath("./oos:priceInfo/oos:currency/oos:code", namespaces=self.nsmp))
                self.price_rur = ParsingTools.get_val_from_node(child.xpath("./oos:priceInfo/oos:priceRUR", namespaces=self.nsmp), is_num=True)
            self.customer = ParsingTools.get_val_from_node(child.xpath("./oos:customer/oos:regNum", namespaces=self.nsmp))
            if self.customer:
                self.customer_xpath = self.tree.getpath(child.xpath("./oos:customer/oos:regNum", namespaces=self.nsmp)[0])
            self.customer_inn = ParsingTools.check_inn(ParsingTools.get_val_from_node(child.xpath("./oos:customer/oos:inn", namespaces=self.nsmp)))
            self.customer_kpp = ParsingTools.check_kpp(ParsingTools.get_val_from_node(child.xpath("./oos:customer/oos:kpp", namespaces=self.nsmp)))
            if self.customer_inn:
                self.customer_xpath = self.tree.getpath(child.xpath("./oos:customer/oos:inn", namespaces=self.nsmp)[0])
            if len(child.xpath("./oos:foundation/oos:fcsOrder", namespaces=self.nsmp)) != 0:
                if len(child.xpath("./oos:foundation/oos:fcsOrder/oos:order", namespaces=self.nsmp)) != 0:
                    self.purchasenumber = ParsingTools.get_val_from_node(child.xpath("./oos:foundation/oos:fcsOrder/oos:order/oos:notificationNumber", namespaces=self.nsmp))
                    self.lotnumber = ParsingTools.get_val_from_node(child.xpath("./oos:foundation/oos:fcsOrder/oos:order/oos:lotNumber", namespaces=self.nsmp)) or '1'
                else:
                    self.purchasenumber = ParsingTools.get_val_from_node(child.xpath("./oos:foundation/oos:fcsOrder/oos:notificationNumber", namespaces=self.nsmp))
                    self.lotnumber = ParsingTools.get_val_from_node(child.xpath("./oos:foundation/oos:fcsOrder/oos:lotNumber", namespaces=self.nsmp)) or '1'
                self.law = '44'
            elif len(child.xpath("./oos:foundation/oos:oosOrder", namespaces=self.nsmp)) != 0:
                if len(child.xpath("./oos:foundation/oos:oosOrder/oos:order", namespaces=self.nsmp)) != 0:
                    self.purchasenumber = ParsingTools.get_val_from_node(child.xpath("./oos:foundation/oos:oosOrder/oos:order/oos:notificationNumber", namespaces=self.nsmp))
                    self.lotnumber = ParsingTools.get_val_from_node(child.xpath("./oos:foundation/oos:oosOrder/oos:order/oos:lotNumber", namespaces=self.nsmp)) or '1'
                else:
                    self.purchasenumber = ParsingTools.get_val_from_node(child.xpath("./oos:foundation/oos:oosOrder/oos:notificationNumber", namespaces=self.nsmp))
                    self.lotnumber = ParsingTools.get_val_from_node(child.xpath("./oos:foundation/oos:oosOrder/oos:lotNumber", namespaces=self.nsmp)) or '1'
                self.law = '94'
            else:
                self.purchasenumber = None
                self.lotnumber = None
                self.law = None
            print(self.law)
            print(self.purchasenumber, self.lotnumber)
            if self.contract_xml_type == 'contractCancel':
                self.stage = 'IN'
            else:
                self.stage = ParsingTools.get_val_from_node(child.xpath("./oos:currentContractStage", namespaces=self.nsmp))
            if len(child.xpath("./oos:enforcement/oos:bankGuarantee", namespaces=self.nsmp)) != 0:
                self.enforcement = 'guarantee'
                self.enforcement_amount = ParsingTools.get_val_from_node(child.xpath("./oos:enforcement/oos:bankGuarantee/oos:guaranteeAmount", namespaces=self.nsmp), is_num=True)
                self.enforcement_currency = ParsingTools.get_val_from_node(child.xpath("./enforcement/oos:bankGuarantee/oos:currency/oos:code", namespaces=self.nsmp))
            elif len(child.xpath("./oos:enforcement/oos:cashAccount", namespaces=self.nsmp)) != 0:
                self.enforcement = 'cash'
                self.enforcement_amount = ParsingTools.get_val_from_node(child.xpath("./oos:enforcement/oos:cashAccount/oos:amount", namespaces=self.nsmp), is_num=True)
                self.enforcement_currency = ParsingTools.get_val_from_node(child.xpath("./oos:enforcement/oos:cashAccount/oos:currency/oos:code", namespaces=self.nsmp))
            else:
                self.enforcement = None
                self.enforcement_amount = None
                self.enforcement_currency = None
            suppliers_data = child.xpath("./oos:suppliers/oos:supplier", namespaces=self.nsmp)
            self.suppliers = []
            if int(self.schemaversion['schemeVersion'][0]) < 5:
                for supplier in suppliers_data:
                    supplier_dict= {}
                    supplier_dict['xpath'] = self.tree.getpath(supplier)
                    supplier_dict['participant_type'] = ParsingTools.get_val_from_node(supplier.xpath("./oos:participantType", namespaces=self.nsmp))
                    supplier_dict['inn'] = ParsingTools.check_inn(ParsingTools.get_val_from_node(supplier.xpath("./oos:inn", namespaces=self.nsmp)))
                    supplier_dict['kpp'] = ParsingTools.check_kpp(ParsingTools.get_val_from_node(supplier.xpath("./oos:kpp", namespaces=self.nsmp)))
                    supplier_dict['ogrn'] = ParsingTools.check_ogrn(ParsingTools.get_val_from_node(supplier.xpath("./oos:ogrn", namespaces=self.nsmp)))
                    supplier_dict['orgname'] = ParsingTools.get_val_from_node(supplier.xpath("./oos:organizationName", namespaces=self.nsmp))
                    supplier_dict['id_number'] = ParsingTools.get_val_from_node(supplier.xpath("./oos:idNumber",namespaces=self.nsmp))
                    supplier_dict['lastname'] = ParsingTools.get_val_from_node(supplier.xpath("./oos:contactInfo/oos:lastName", namespaces=self.nsmp))
                    supplier_dict['firstname'] = ParsingTools.get_val_from_node(supplier.xpath("./oos:contactInfo/oos:firstName", namespaces=self.nsmp))
                    supplier_dict['middlename'] = ParsingTools.get_val_from_node(supplier.xpath("./oos:contactInfo/oos:middleName", namespaces=self.nsmp))
                    supplier_dict['email'] = ParsingTools.get_val_from_node(supplier.xpath("./oos:contactEMail", namespaces=self.nsmp))
                    supplier_dict['phone'] = ParsingTools.get_val_from_node(supplier.xpath("./oos:contactPhone", namespaces=self.nsmp))
                    supplier_dict['fax'] = ParsingTools.get_val_from_node(supplier.xpath("./oos:contactFax", namespaces=self.nsmp))
                    self.suppliers.append(supplier_dict)
                    break
            else:
                for supplier in suppliers_data:
                    for sup_legal in supplier.xpath("./oos:legalEntityRF", namespaces=self.nsmp):
                        supplier_dict = {}
                        supplier_dict['xpath'] = self.tree.getpath(sup_legal)
                        supplier_dict['participant_type'] = 'U'
                        supplier_dict['inn'] = ParsingTools.check_inn(ParsingTools.get_val_from_node(sup_legal.xpath("./oos:INN",namespaces=self.nsmp)))
                        supplier_dict['kpp'] = ParsingTools.check_kpp(ParsingTools.get_val_from_node(sup_legal.xpath("./oos:KPP",namespaces=self.nsmp)))
                        supplier_dict['ogrn'] = ParsingTools.check_ogrn(ParsingTools.get_val_from_node(sup_legal.xpath("./oos:OGRN",namespaces=self.nsmp)))
                        supplier_dict['orgname'] = ParsingTools.get_val_from_node(sup_legal.xpath("./oos:fullName", namespaces=self.nsmp))
                        supplier_dict['id_number'] = ParsingTools.get_val_from_node(sup_legal.xpath("./oos:idNumber",namespaces=self.nsmp))
                        supplier_dict['lastname'] = ParsingTools.get_val_from_node(sup_legal.xpath("./oos:contactInfo/oos:lastName", namespaces=self.nsmp))
                        supplier_dict['firstname'] = ParsingTools.get_val_from_node(sup_legal.xpath("./oos:contactInfo/oos:firstName", namespaces=self.nsmp))
                        supplier_dict['middlename'] = ParsingTools.get_val_from_node(sup_legal.xpath("./oos:contactInfo/oos:middleName", namespaces=self.nsmp))
                        supplier_dict['email'] = ParsingTools.get_val_from_node(sup_legal.xpath("./oos:contactEMail", namespaces=self.nsmp))
                        supplier_dict['phone'] = ParsingTools.get_val_from_node(sup_legal.xpath("./oos:contactPhone", namespaces=self.nsmp))
                        supplier_dict['fax'] = ParsingTools.get_val_from_node(sup_legal.xpath("./oos:contactFax",namespaces=self.nsmp))
                        self.suppliers.append(supplier_dict)
                        break
                    for sup_person in supplier.xpath("./oos:individualPersonRF", namespaces=self.nsmp):
                        supplier_dict = {}
                        supplier_dict['xpath'] = self.tree.getpath(sup_person)
                        supplier_dict['participant_type'] = 'P'
                        supplier_dict['inn'] = ParsingTools.check_inn(ParsingTools.get_val_from_node(sup_person.xpath("./oos:INN",namespaces=self.nsmp)))
                        supplier_dict['kpp'] = None
                        supplier_dict['ogrn'] = None
                        supplier_dict['orgname'] = None
                        supplier_dict['id_number'] = ParsingTools.get_val_from_node(sup_person.xpath("./oos:idNumber",namespaces=self.nsmp))
                        supplier_dict['lastname'] = ParsingTools.get_val_from_node(sup_person.xpath("./oos:lastName", namespaces=self.nsmp))
                        supplier_dict['firstname'] = ParsingTools.get_val_from_node(sup_person.xpath("./oos:firstName", namespaces=self.nsmp))
                        supplier_dict['middlename'] = ParsingTools.get_val_from_node(sup_person.xpath("./oos:middleName", namespaces=self.nsmp))
                        supplier_dict['email'] = ParsingTools.get_val_from_node(sup_person.xpath("./oos:contactEMail", namespaces=self.nsmp))
                        supplier_dict['phone'] = ParsingTools.get_val_from_node(sup_person.xpath("./oos:contactPhone", namespaces=self.nsmp))
                        supplier_dict['fax'] = ParsingTools.get_val_from_node(sup_person.xpath("./oos:contactFax", namespaces=self.nsmp))
                        self.suppliers.append(supplier_dict)
                        break
                    for sup_foreign_legal in supplier.xpath("./oos:legalEntityForeignState", namespaces=self.nsmp):
                        supplier_dict = {}
                        supplier_dict['xpath'] = self.tree.getpath(sup_foreign_legal)
                        supplier_dict['participant_type'] = 'UF'
                        supplier_dict['inn'] = None
                        supplier_dict['kpp'] = None
                        supplier_dict['ogrn'] = None
                        supplier_dict['orgname'] = ParsingTools.get_val_from_node(sup_foreign_legal.xpath("./oos:fullName", namespaces=self.nsmp))
                        supplier_dict['id_number'] = ParsingTools.get_val_from_node(sup_foreign_legal.xpath("./oos:idNumber",namespaces=self.nsmp))
                        supplier_dict['lastname'] = None
                        supplier_dict['firstname'] = None
                        supplier_dict['middlename'] = None
                        supplier_dict['email'] = None
                        supplier_dict['fax'] = None
                        self.suppliers.append(supplier_dict)
                        break
                    for sup_foreign_person in supplier.xpath("./oos:individualPersonForeignState", namespaces=self.nsmp):
                        supplier_dict = {}
                        supplier_dict['xpath'] = self.tree.getpath(sup_foreign_person)
                        supplier_dict['participant_type'] = 'PF'
                        supplier_dict['inn'] = None
                        supplier_dict['kpp'] = None
                        supplier_dict['ogrn'] = None
                        supplier_dict['orgname'] = None
                        supplier_dict['id_number'] = ParsingTools.get_val_from_node(sup_foreign_person.xpath("./oos:idNumber", namespaces=self.nsmp))
                        supplier_dict['lastname'] = ParsingTools.get_val_from_node(sup_foreign_person.xpath("./oos:lastName", namespaces=self.nsmp))
                        supplier_dict['firstname'] = ParsingTools.get_val_from_node(sup_foreign_person.xpath("./oos:firstName", namespaces=self.nsmp))
                        supplier_dict['middlename'] = ParsingTools.get_val_from_node(sup_foreign_person.xpath("./oos:middleName", namespaces=self.nsmp))
                        supplier_dict['email'] = None
                        supplier_dict['phone'] = None
                        supplier_dict['fax'] = None
                        self.suppliers.append(supplier_dict)
                        break
            product_data = child.xpath("./oos:products/oos:product", namespaces=self.nsmp)
            self.products = []
            for product in product_data:
                product_dict = {}
                product_dict['okpd_code'] = ParsingTools.get_val_from_node(product.xpath("./oos:OKPD/oos:code", namespaces=self.nsmp))
                product_dict['okpd2_code'] = ParsingTools.get_val_from_node(product.xpath("./oos:OKPD2/oos:code", namespaces=self.nsmp))
                product_dict['name'] = ParsingTools.get_val_from_node(product.xpath("./oos:name", namespaces=self.nsmp))
                self.products.append(product_dict)
            self.put_data_to_db()

    def put_data_to_db(self):
        logname = 'Contract_loader' + self.filename
        print(self.filename)
        db_logger = LoggerDb(log_name=logname, log_file=CONTRACT_LOG_FILE, job='Contract')
        if self.purchasenumber:
            notification = Notifications.get_notification_data(self.purchasenumber, self.lotnumber, self.law,
                                                               db_logger, self.purchasenumber, self.filename)
            print('Notification =', notification._id)
        else:
            notification = Notifications()
        # get customer legal_id
        customer_from_registry = RegistryCustomers.get_customer_data(self.customer, self.law)
        if customer_from_registry._legal:
            customer = Customers.get_customer_data(notification, customer_from_registry._legal_id, db_logger, self.customer_xpath,
                                               self.filename, self.regnumber)
            print('Customer =', customer._id)
        else:
            if self.customer_inn:
                legal_customer = Legals.getLegaldata(self.customer_inn, None, None, self.customer_kpp, 'goverment',
                                                     self.customer_xpath, db_logger, self.filename)
                customer = Customers.get_customer_data(notification, legal_customer._id, db_logger,
                                                       self.customer_xpath,
                                                       self.filename, self.regnumber)
            else:
                customer = Customers()
        supplier = Legals()
        # get supplier data
        for supp in self.suppliers:
            contact_data = supp.copy()
            for key in supp:
                if key not in ['lastname', 'firstname', 'middlename', 'email', 'phone', 'fax']:
                    contact_data.pop(key)
                elif key in ['phone', 'fax']:
                    contact_data.update({key: ParsingTools.check_phone_num(contact_data[key])})
            #print(contact_data)
            if supp.get('inn') and len(supp.get('inn')) == 10:
                supplier = Legals.getLegaldata(supp.get('inn'), supp.get('ogrn'),
                                            supp.get('orgname'),
                                            supp.get('kpp'), None,
                                            supp.get('xpath'), db_logger, self.filename)
                print("legal: %s" % supplier._id)
            elif supp['inn'] and len(supp['inn']) == 12:
                if supp['lastname']:
                    supplier = Legals.getLegaldata(supp.get('inn'), supp.get('ogrn'),
                                                supp.get('orgname'), supp.get('kpp'),
                                                "individual",
                                                supp.get('xpath'), db_logger,
                                                self.filename,
                                                supp['lastname'],
                                                supp['firstname'],
                                                supp['middlename'])
                else:
                    supplier = Legals.getLegaldata(supp.get('inn'), supp.get('ogrn'),
                                                supp.get('orgname'), supp.get('kpp'),
                                                "individual",
                                                supp.get('xpath'), db_logger,self.filename)
                print("legal: %s" % supplier._id)
            elif not supp['inn'] and (
                    supp['participant_type'] in ['UF', 'PF'] or supp['id_number']):
                supplier = Legals.getLegaldata(None, None,
                                            supp.get('orgname'), None, "foreign",
                                            supp.get('xpath'), db_logger, self.filename)
                print("legal: %s" % supplier._id)


        contract = Contracts.get_contract_data(notification._id, customer._id, self.regnumber, self.publishdate, self.signdate,
                            self.enddate, self.price, self.price_rur, self.currency, self.stage, self.enforcement,
                            self.enforcement_amount, self.enforcement_currency, supplier._id, db_logger, self.filename,
                            self.regnumber_xpath, self.law)
        print('Contract =',contract._id)
        for p in self.products:
            product = ContractsProducts.update_products(contract._id, p['okpd_code'], p['okpd2_code'],
                                                        p['name'],self.publishdate)
            if product:
                print('Product=', product._id)
        if supplier._id:
            contact = Contacts.update_contact_data(contract._id, supplier._id, contact_data, self.publishdate)

        db_logger.close_log()


if __name__ == '__main__':
    parser = ContractParser(r'C:\Test.Zakupki.local\fcs_regions\Altaj_Resp\contracts\contractProcedure_0137200002113000012_50777108.xml')