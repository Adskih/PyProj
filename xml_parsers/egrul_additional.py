"""
Вспомогательный модуль для загрузчика ЕГРЮЛ
"""


class EgrulFields:
    def __init__(self):
        self.inn = None
        self.ogrn = None
        self.fulltitle = None
        self.shorttitle = None
        self.ogrn_date = None
        self.okopf_code = None
        self.actuality = None
        self.capital = None
        self.kpp = None
        self.postalcode = None
        self.region_code = None
        self.kladr_code = None
        self.region_type = None
        self.region_name = None
        self.district_type = None
        self.district_name = None
        self.city_type = None
        self.city_name = None
        self.community_type = None
        self.community_name = None
        self.street_type = None
        self.street_name = None
        self.house = None
        self.building = None
        self.flat = None
        self.head_position_date = None
        self.head_firstname = None
        self.head_inn = None
        self.head_position_type = None
        self.head_position_name = None
        self.head_lastname = None
        self.head_position_code = None
        self.head_middlename = None
        self.f_legal_inn = None
        self.f_legal_part_percent = None
        self.f_legal_part_amount = None
        self.f_legal_ogrn = None
        self.f_legal_fulltitle = None
        self.f_person_part_percent = None
        self.f_person_lastname = None
        self.f_person_part_amount = None
        self.f_person_firstname = None
        self.f_person_inn = None
        self.f_person_middlename = None
        self.f_flegal_part_percent = None
        self.f_flegal_fulltitle = None
        self.f_flegal_part_amount = None
        self.f_flegal_inn = None
        self.f_flegal_ogrn = None
        self.external_ogrn = None
        self.external_fulltitle = None
        self.f_gmu_part_amount = None
        self.f_gmu_fulltitle = None
        self.f_gmu_part_percent = None
        self.f_gmu_region_name = None
        self.f_gmu_region_code = None
        self.external_inn = None
        self.manage_ogrn = None
        self.f_pif_fulltitle = None
        self.f_pif_part_percent = None
        self.manage_fulltitle = None
        self.manage_inn = None
        self.f_pif_part_amount = None
        self.filial_fulltitle = None
        self.filial_kpp = None
        self.podrazd_fulltitle = None
        self.podrazd_kpp = None