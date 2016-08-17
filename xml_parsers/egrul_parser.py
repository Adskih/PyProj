"""
Загрузчик ЕГРЮЛ
"""
import os
import lxml.etree as etree
from loger_pack.logger import LoggerDb
from loger_pack import EGUL_LOG_FILE
from xml_parsers.parsing_tools import ParsingTools, Types
import datetime
from model_pckg.model import Legals, LegalsAddresses, LegalsFounders, LegalsHeads, Persons
from xml_parsers.egrul_additional import EgrulFields



class EgrulParser(EgrulFields):
    def __init__(self, file):
        EgrulFields.__init__(self)
        self.legal_dict = {
            'ogrn': {'path': './@ОГРН', 'type': Types.string},
            'inn': {'path': './@ИНН', 'type': Types.string},
            'kpp': {'path': './@КПП', 'type': Types.string},
            'ogrn_date':  {'path': './@ДатаОГРН', 'type': Types.date},
            'okopf_code': {'path': './@КодОПФ', 'type': Types.string},
            'actuality': {'path': './@ДатаВып', 'type': Types.date},
            'capital': {'path': './СвУстКап/@СумКап', 'type': Types.number},
            'shorttitle': {'path': './СвНаимЮЛ/@НаимЮЛСокр', 'type': Types.string},
            'fulltitle': {'path': './СвНаимЮЛ/@НаимЮЛПолн', 'type': Types.string},
            'postalcode': {'path': 'СвАдресЮЛ/АдресРФ/@Индекс', 'type': Types.string},
            'region_code': {'path': './CвАдресЮЛ/АдресРФ/@КодРегион', 'type': Types.string},
            'kladr_code': {'path': './СвАдресЮЛ/АдресРФ/@КодАдрКладр', 'type': Types.string},
            'region_type': {'path': './СвАдресЮЛ/АдресРФ/Регион/@ТипРегион', 'type': Types.string},
            'region_name': {'path': './СвАдресЮЛ/АдресРФ/Регион/@НаимРегион', 'type': Types.string},
            'district_type': {'path': './СвАдресЮЛ/АдресРФ/Район/@ТипРайон', 'type': Types.string},
            'district_name': {'path': './СвАдресЮЛ/АдресРФ/Район/@НаимРайон', 'type': Types.string},
            'city_type': {'path': './СвАдресЮЛ/АдресРФ/Город/@ТипГород', 'type': Types.string},
            'city_name': {'path': './СвАдресЮЛ/АдресРФ/Город/@НаимГород', 'type': Types.string},
            'community_type': {'path': './СвАдресЮЛ/АдресРФ/НаселПункт/@ТипНаселПункт', 'type': Types.string},
            'community_name': {'path': './СвАдресЮЛ/АдресРФ/НаселПункт/@НаимНаселПункт', 'type': Types.string},
            'street_type': {'path': './СвАдресЮЛ/АдресРФ/Улица/@ТипУлица', 'type': Types.string},
            'street_name': {'path': './СвАдресЮЛ/АдресРФ/Улица/@НаимУлица', 'type': Types.string},
            'house': {'path': './СвАдресЮЛ/АдресРФ/@Дом', 'type': Types.string},
            'building': {'path': './СвАдресЮЛ/АдресРФ/@Корпус', 'type': Types.string},
            'flat': {'path': './СвАдресЮЛ/АдресРФ/@Кварт', 'type': Types.string}
        }
        self.heads_dict = {
            'head_lastname': {'path': './СвФЛ/@Фамилия', 'type': Types.string},
            'head_firstname': {'path': './СвФЛ/@Имя', 'type': Types.string},
            'head_middlename': {'path': './СвФЛ/@Отчество', 'type': Types.string},
            'head_inn': {'path': './СвФЛ/@ИННФЛ', 'type': Types.string},
            'head_position_code': {'path': './СвДолжн/@ВидДолжн', 'type': Types.string},
            'head_position_type': {'path': './СвДолжн/@НаимДолжн', 'type': Types.string},
            'head_position_name': {'path': './СвДолжн/@НаимВидДолжн', 'type': Types.string},
            'head_position_date': {'path': './СвДолжн/ГРНДата/@ДатаЗаписи', 'type': Types.date}
        }
        self.founder_legal_dict = {
            'f_legal_inn': {'path': './НаимИННЮЛ/@ИНН', 'type': Types.string},
            'f_legal_ogrn': {'path': './НаимИННЮЛ/@ОГРН', 'type': Types.string},
            'f_legal_fulltitle': {'path': './НаимИННЮЛ/@НаимЮЛПолн', 'type': Types.string},
            'f_legal_part_percent': {'path': './ДоляУстКап/РазмерДоли/Процент', 'type': Types.number},
            'f_legal_part_amount': {'path': './ДоляУстКап/@НоминСтоим', 'type': Types.number},
        }
        self.founder_person_dict = {
            'f_person_lastname': {'path': './СвФЛ/@Фамилия', 'type': Types.string},
            'f_person_firstname': {'path': './СвФЛ/@Имя', 'type': Types.string},
            'f_person_middlename': {'path': './СвФЛ/@Отчество', 'type': Types.string},
            'f_person_inn': {'path': './СвФЛ/@ИННФЛ', 'type': Types.string},
            'f_person_part_percent': {'path': './ДоляУстКап/РазмерДоли/Процент', 'type': Types.number},
            'f_person_part_amount': {'path': './ДоляУстКап/@НоминСтоим', 'type': Types.number}
        }
        self.founder_flegal_dict = {
            'f_flegal_inn': {'path': './НаимИННЮЛ/@ИНН', 'type': Types.string},
            'f_flegal_ogrn': {'path': './НаимИННЮЛ/@ОГРН', 'type': Types.string},
            'f_flegal_fulltitle': {'path': './НаимИННЮЛ/@НаимЮЛПолн', 'type': Types.string},
            'f_flegal_part_percent': {'path': './ДоляУстКап/РазмерДоли/Процент', 'type': Types.number},
            'f_flegal_part_amount': {'path': './ДоляУстКап/@НоминСтоим', 'type': Types.number}
        }
        self.founder_gmu_dict = {
            'f_gmu_fulltitle': {'path': './ВидНаимУчр/@НаимМО', 'type': Types.string},
            'f_gmu_part_percent': {'path': './ДоляУстКап/РазмерДоли/Процент', 'type': Types.number},
            'f_gmu_part_amount': {'path': './ДоляУстКап/@НоминСтоим', 'type': Types.number},
            'f_gmu_region_code': {'path': './ВидНаимУчр/@КодРегион', 'type': Types.string},
            'f_gmu_region_name': {'path': './ВидНаимУчр/@НаимРегион', 'type': Types.string},
            'external_inn': {'path': './СвОргОсущПр/НаимИННЮЛ/@ИНН', 'type': Types.string},
            'external_ogrn': {'path': './СвОргОсущПр/НаимИННЮЛ/@ОГРН', 'type': Types.string},
            'external_fulltitle': {'path': './СвОргОсущПр/НаимИННЮЛ/@НаимЮЛПолн', 'type': Types.string}
        }
        self.founder_pif_dict = {
            'f_pif_fulltitle': {'path': './СвНаимПИФ/@НаимПИФ', 'type': Types.string},
            'f_pif_part_percent': {'path': './ДоляУстКап/РазмерДоли/Процент', 'type': Types.number},
            'f_pif_part_amount': {'path': './ДоляУстКап/@НоминСтоим', 'type': Types.number},
            'manage_inn': {'path': './СвУпрКомпПИФ/УпрКомпПиф/@ИНН', 'type': Types.string},
            'manage_ogrn': {'path': './СвУпрКомпПИФ/УпрКомпПиф/@ОГРН', 'type': Types.string},
            'manage_fulltitle': {'path': './СвУпрКомпПИФ/УпрКомпПиф/@НаимЮЛПолн', 'type': Types.string}
        }
        self.filial_dict = {
            'filial_kpp': {'path': './СвУчетНОФилиал/@КПП', 'type': Types.string},
            'filial_fulltitle': {'path': './СвНаим/@НаимПолн', 'type': Types.string}
        }
        self.podrazd_dict = {
            'podrazd_kpp': {'path': './СвУчетНОПредстав/@КПП', 'type': Types.string},
            'podrazd_fulltitle': {'path': './СвНаим/@НаимПолн', 'type': Types.string}
        }
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
        for child in self.root:
            ParsingTools.get_values_from_xml(self, child, self.legal_dict)
            self.ogrn = ParsingTools.check_ogrn(self.ogrn)
            self.inn = ParsingTools.check_inn(self.inn)
            self.kpp = ParsingTools.check_kpp(self.kpp)
            self.ogrn_xpath = ParsingTools.get_xpath(self.tree, child, './@ОГРН')
            self.heads_list = []
            self.founders_legals_list = []
            self.founders_persons_list = []
            self.founder_foreign_list = []
            self.founder_gmu_list = []
            self.founder_pif_list = []
            self.filial_list = []
            for head in child.xpath('./СведДолжнФЛ'):
                ParsingTools.get_values_from_xml(self, head, self.heads_dict)
                self.head_inn = ParsingTools.check_inn(self.head_inn)
                _head = {
                    'lastname': self.head_lastname,
                    'firstname': self.head_firstname,
                    'middlename': self.head_middlename,
                    'inn': self.head_inn,
                    'position_code': self.head_position_code,
                    'position_type': self.head_position_type,
                    'position_name': self.head_position_name,
                    'position_date': self.head_position_date
                }
                self.heads_list.append(_head)

            for founder_legal in child.xpath('./СвУчредит/УчрЮЛРос'):
                ParsingTools.get_values_from_xml(self, founder_legal, self.founder_legal_dict)
                self.f_legal_inn = ParsingTools.check_inn(self.f_legal_inn)
                self.f_legal_ogrn = ParsingTools.check_ogrn(self.f_legal_ogrn)
                _founder_legal = {
                    'inn': self.f_legal_inn,
                    'ogrn': self.f_legal_ogrn,
                    'fulltitle': self.f_legal_fulltitle,
                    'percent': self.f_legal_part_percent,
                    'amount': self.f_legal_part_amount
                }
                self.founders_legals_list.append(_founder_legal)

            for founder_person in child.xpath('./СвУчредит/УчрФЛ'):
                ParsingTools.get_values_from_xml(self, founder_person, self.founder_person_dict)
                self.f_person_inn = ParsingTools.check_inn(self.f_person_inn)
                _founder_person = {
                    'inn': self.f_person_inn,
                    'lastname': self.f_person_lastname,
                    'fisrtname': self.f_person_firstname,
                    'middlename': self.f_person_middlename,
                    'percent': self.f_person_part_percent,
                    'amount': self.f_person_part_amount
                }
                self.founders_persons_list.append(_founder_person)
            for founder_foreign in child.xpath('./СвУчредит/УчрЮЛИн'):
                ParsingTools.get_values_from_xml(self, founder_foreign, self.founder_flegal_dict)
                self.f_flegal_inn = ParsingTools.check_inn(self.f_flegal_inn)
                self.f_flegal_ogrn = ParsingTools.check_ogrn(self.f_flegal_ogrn)
                _founder_foreign = {
                    'inn': self.f_flegal_inn,
                    'ogrn': self.f_flegal_ogrn,
                    'fulltitle': self.f_flegal_fulltitle,
                    'percent': self.f_flegal_part_percent,
                    'amount': self.f_flegal_part_amount
                }
                self.founder_foreign_list.append(_founder_foreign)
            for founder_gmu in child.xpath('./СвУчредит/УчрРФСубМО'):
                ParsingTools.get_values_from_xml(self, founder_gmu, self.founder_gmu_dict)
                _founder_gmu = {
                    'fulltitle': self.f_gmu_fulltitle,
                    'percent': self.f_gmu_part_percent,
                    'amount': self.f_gmu_part_amount,
                    'region_code': self.f_gmu_region_code,
                    'region_name': self.f_gmu_region_name,
                    'external_inn': self.external_inn,
                    'external_ogrn': self.external_ogrn,
                    'external_fulltitle': self.external_fulltitle
                }
                self.founder_gmu_list.append(_founder_gmu)
            for founder_pif in child.xpath('./СвУчредит/УчрПИФ'):
                ParsingTools.get_values_from_xml(self, founder_pif, self.founder_pif_dict)
                self.manage_inn = ParsingTools.check_inn(self.manage_inn)
                self.manage_ogrn = ParsingTools.check_ogrn(self.manage_ogrn)
                _founder_pif = {
                    'fulltitle': self.f_pif_fulltitle,
                    'percent': self.f_pif_part_percent,
                    'amount': self.f_pif_part_amount,
                    'manage_inn': self.manage_inn,
                    'manage_ogrn': self.manage_ogrn,
                    'manage_fulltitle': self.manage_fulltitle
                }
                self.founder_pif_list.append(_founder_pif)
            for filial in child.xpath('./СвПодразд/СвФилиал'):
                ParsingTools.get_values_from_xml(self, filial, self.filial_dict)
                _filial = {
                    'kpp': self.filial_kpp,
                    'fulltitile': self.filial_fulltitle
                }
                self.filial_list.append(_filial)
            for podrazd in child.xpath('./СвПодразд/СвПредстав'):
                ParsingTools.get_values_from_xml(self, podrazd, self.podrazd_dict)
                _podrazd = {
                    'kpp': self.podrazd_kpp,
                    'fulltitile': self.podrazd_fulltitle
                }
                self.filial_list.append(_podrazd)
            self.put_data_to_db()


    def put_data_to_db(self):
        logname = 'EGRUL_loader' + self.filename
        db_logger = LoggerDb(log_name=logname, log_file=EGUL_LOG_FILE, job='Egrul')
        organization = Legals.put_egrul_data(self.inn, self.ogrn, self.kpp, self.fulltitle, self.capital, self.okopf_code,
                                           self.ogrn_date, 'legal',self.actuality, db_logger, self.ogrn_xpath, self.filename,
                                            self.shorttitle)
        print(organization._id)

        address = LegalsAddresses.update_address_data(organization._id,self.postalcode, self.region_code, self.kladr_code, self.region_type,
                                                      self.region_name, self.district_type, self.district_name,
                                                      self.city_type, self.city_name, self.community_type, self.community_name,
                                                      self.street_type, self.street_name, self.house, self.building, self.flat)
        db_logger.close_log()


if __name__ == '__main__':
    EgrulParser(r'C:\Test.Zakupki.local\EGRUL_FULL_2015-08-29_23265.XML')