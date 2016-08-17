import os
import lxml.etree as etree
from loger_pack import PROTOCOL_LOG_FILE
from loger_pack.logger import LoggerDb
from model_pckg.model import Protocols, Legals, Participants, ParsingTools, Notifications, Winners


class ProtocolParser:
    "Обработчик протоколов электронного аукциона"
    def __init__(self, file):
        self.file_is_empty = False
        self.file = file
        try:
            self.tree = etree.parse(file)
            self.filename = file.split(os.sep, -1)[-1:][0]
            self.getMainNodes()
        except etree.XMLSyntaxError:
            self.file_is_empty = True
            print("File %s is empty!" % file)


    def getMainNodes(self):
        "Get data from the top of xml"
        self.root = self.tree.getroot()
        self.nsmp = {'export': 'http://zakupki.gov.ru/oos/types/1', 'ns2': 'http://zakupki.gov.ru/oos/export/1', 'ns3': "http://zakupki.gov.ru/oos/printform/1"}
        self.protocol_type = ParsingTools.get_node_name(self.root)  # Gets name of first child
        print(self.protocol_type)
        self.purchasenumber = ParsingTools.get_val_from_node(self.root.xpath("./*/export:purchaseNumber", namespaces=self.nsmp))
        self.purchasenumber_xpath = self.tree.getpath(self.root.xpath("./*/export:purchaseNumber", namespaces=self.nsmp)[0])
        self.protocolnum = ParsingTools.get_val_from_node(self.root.xpath("./*/export:protocolNumber", namespaces=self.nsmp))
        if self.protocolnum:
            self.protocolnum_xpath = self.tree.getpath(self.root.xpath("./*/export:protocolNumber", namespaces=self.nsmp)[0])
        self.protocol_date = ParsingTools.get_val_from_node(self.root.xpath("./*/export:protocolDate", namespaces=self.nsmp), is_date=True)
        self.sign_date = ParsingTools.get_val_from_node(self.root.xpath("./*/export:signDate", namespaces=self.nsmp), is_date=True)
        self.publishdate = ParsingTools.get_val_from_node(self.root.xpath("./*/export:publishDate", namespaces=self.nsmp), is_date=True)
        self.docpublishdate = ParsingTools.get_val_from_node(self.root.xpath("./*/export:docPublishDate", namespaces=self.nsmp), is_date=True)
        self.protocol_lots = self.root.xpath("//export:protocolLot", namespaces=self.nsmp)
        if self.purchasenumber and not self.purchasenumber.startswith('991111'):
            self.getLotData()


    def getLotData(self):
        "Get data from 'parotocolLot' Node"
        self.lot_data = {}
        if self.protocol_type == 'fcsProtocolCancel':
            self.put_cancel_protocol()
        for lot in self.protocol_lots:
            self.lotnumber = ParsingTools.get_val_from_node(lot.xpath("./export:lotNUmber", namespaces=self.nsmp)) or 1
            self.participants = lot.xpath("//export:application", namespaces=self.nsmp)
            self.is_participant_impersonal = True if len(lot.xpath("//export:application/export:appParticipant", namespaces=self.nsmp)) == 0 else False
            self.is_abandoned = False if len(lot.xpath("./export:abandonedReason", namespaces=self.nsmp)) == 0 else True
            self.participants_list = []
            for participant in self.participants:
                participant_dict={}
                participant_dict['journal_number'] = ParsingTools.get_val_from_node(participant.xpath("./export:journalNumber", namespaces=self.nsmp))
                participant_dict['xpath'] = self.tree.getpath(participant)
                participant_dict['app_date'] = ParsingTools.get_val_from_node(participant.xpath("./export:appDate", namespaces=self.nsmp), is_date=True)
                participant_dict['participant_type'] = ParsingTools.get_val_from_node(participant.xpath("./export:appParticipant/export:participantType", namespaces=self.nsmp))
                participant_dict['inn'] = ParsingTools.check_inn(ParsingTools.get_val_from_node(participant.xpath("./export:appParticipant/export:inn", namespaces=self.nsmp)))
                participant_dict['kpp'] = ParsingTools.check_kpp(ParsingTools.get_val_from_node(participant.xpath("./export:appParticipant/export:kpp", namespaces=self.nsmp)))
                participant_dict['ogrn'] = ParsingTools.check_ogrn(ParsingTools.get_val_from_node(participant.xpath("./export:appParticipant/export:ogrn", namespaces=self.nsmp)))
                participant_dict['id_number'] = ParsingTools.get_val_from_node(participant.xpath("./export:appParticipant/export:idNumber", namespaces=self.nsmp))
                participant_dict['orgname'] = ParsingTools.get_val_from_node(participant.xpath("./export:appParticipant/export:organizationName", namespaces=self.nsmp))
                participant_dict['firmname'] = ParsingTools.get_val_from_node(participant.xpath("./export:appParticipant/export:firmName", namespaces=self.nsmp))
                participant_dict['admitted'] = ParsingTools.get_val_from_node(participant.xpath("./export:admitted", namespaces=self.nsmp), is_bool=True)
                participant_dict['lastname'] = ParsingTools.get_val_from_node(participant.xpath("./export:appParticipant/export:contactInfo/export:lastName", namespaces=self.nsmp))
                participant_dict['firstname'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:appParticipant/export:contactInfo/export:firstName", namespaces=self.nsmp))
                participant_dict['middlename'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:appParticipant/export:contactInfo/export:middleName", namespaces=self.nsmp))
                participant_dict['admitted_result'] = ParsingTools.get_val_from_node(participant.xpath("./export:admittedInfo/export:resultType", namespaces=self.nsmp))
                participant_dict['included'] = ParsingTools.get_val_from_node(participant.xpath("./export:admittedInfo/export:included", namespaces=self.nsmp), is_bool=True)
                participant_dict['appratting'] = ParsingTools.get_val_from_node(participant.xpath("./export:appRating", namespaces=self.nsmp))
                participant_dict['offer_price'] = ParsingTools.get_val_from_node(participant.xpath("./export:priceOffers/export:lastOffer/export:price", namespaces=self.nsmp), is_num=True)
                #Только для протоколов ЗП
                participant_dict['offer_price_zp'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:lastOffer/export:price", namespaces=self.nsmp), is_num=True)
                # Только для протоколов ЗК И ЗП
                participant_dict['offer_price_zk'] = ParsingTools.get_val_from_node(participant.xpath("./export:price", namespaces=self.nsmp), is_num=True)
                participant_dict['offer_date_zp'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:lastOffer/export:date", namespaces=self.nsmp), is_date=True)
                participant_dict['offer_date'] = ParsingTools.get_val_from_node(participant.xpath("./export:priceOffers/export:lastOffer/export:date", namespaces=self.nsmp), is_date=True)
                self.participants_list.append(participant_dict)
            self.lot_data.update({self.lotnumber:self.participants_list})
            if self.protocol_type == 'fcsProtocolEvasion':
                self.put_evasion_protocol()
            else:
                self.putXmlDataToDb()


    def putXmlDataToDb(self):
        logname = 'Protocol_loader' + self.filename
        print(self.filename)
        db_logger = LoggerDb(log_name=logname, log_file=PROTOCOL_LOG_FILE, job='protocols')
        for lot in self.lot_data:
            # Get Notification data
            notification = Notifications.get_or_create(regnumber=self.purchasenumber, lotnumber=self.lotnumber, law='44')
            if notification[1]:
                print('INSERT')
                db_logger.write_log('INSERT', 'public.notifications', notification[0]._id, self.filename, self.purchasenumber_xpath)
            print("Notification: %s" % notification[0]._id)
            # Get Protocol data
            protocol = Protocols.getProtocol(notification[0]._id, self.protocolnum, self.publishdate,
                                             self.protocol_date, self.sign_date,
                                             self.protocolnum_xpath, db_logger, self.filename, self.protocol_type,
                                             self.is_abandoned)
            if protocol:
                print("Protocol: %s , %s" % (protocol._id, protocol.publish_date))
                print("Publishdate = ", self.publishdate)
            # Case when several participants participate in tender
            if len(self.lot_data.get(lot))>1:
                for xml_participant in self.lot_data.get(lot):
                    # Protocol EF1 and EF2 have impersonal participants
                    if self.is_participant_impersonal:
                        self.add_impersonal_participant(notification[0]._id, xml_participant, protocol._id)
                    else:

                        participant = self.add_participant_with_legal(notification[0]._id, xml_participant, db_logger,  protocol._id)

                        # is winner IP
                        if xml_participant['admitted'] and xml_participant['appratting'] == '1':
                            self.add_winner(participant, protocol._id, db_logger,
                                            xml_participant.get('xpath'))
            else:
                # Case when only 1 participant participate in tender
                for xml_participant in self.lot_data.get(lot):
                    if self.is_participant_impersonal:
                        self.add_impersonal_participant(notification[0]._id, xml_participant,  protocol._id)
                    else:
                        participant = self.add_participant_with_legal(notification[0]._id, xml_participant, db_logger,  protocol._id)
                        # is winner
                        if participant and xml_participant['admitted']:
                            self.add_winner(participant, protocol._id, db_logger,
                                            xml_participant['xpath'])


        print("-----------------------------------------------------------------------------------------End of work")
        db_logger.close_log()

    def add_impersonal_participant(self, notification, participant, protocol):
        "Legal is unknown"
        print("is_participant_impersonal")
        print("offer_price = ", participant.get('offer_price'))
        participant_ = Participants.saveParticipant(notification, None,
                                                   self.publishdate,
                                                   participant.get('app_date'),
                                                   participant.get('journal_number'),
                                                   participant.get('appratting'),
                                                   participant.get('admitted'),
                                                   participant.get('offer_date'),
                                                   participant.get('offer_price'),
                                                    protocol)
        print("Participant: %s" % participant_.application_number)

    def add_participant_with_legal(self, notification, xml_participant, db_logger, protocol):
        "Personalised applications(legal is known)"
        participant = None
        if xml_participant['inn'] and len(xml_participant['inn']) == 10:
            # Get Legal data about participant
            legal = Legals.getLegaldata(xml_participant.get('inn'), xml_participant.get('ogrn'),
                                        xml_participant.get('orgname'),
                                        xml_participant.get('kpp'), None,
                                        xml_participant['xpath'], db_logger, self.filename)
            print("legal: %s" % legal._id)

            participant = Participants.saveParticipant(notification, legal._id,
                                                        self.publishdate,
                                                        xml_participant.get('app_date'),
                                                        xml_participant.get('journal_number'),
                                                        xml_participant.get('appratting'),
                                                        xml_participant.get('admitted'),
                                                        xml_participant.get('offer_date'),
                                                        xml_participant.get('offer_price'), protocol)

        elif xml_participant['inn'] and len(xml_participant['inn']) == 12:
            if xml_participant['lastname']:
                legal = Legals.getLegaldata(xml_participant.get('inn'), xml_participant.get('ogrn'),
                                            xml_participant.get('orgname'), xml_participant.get('kpp'),
                                            "individual",
                                            xml_participant['xpath'], db_logger, self.filename,
                                            xml_participant['lastname'], xml_participant['firstname'],
                                            xml_participant['middlename'])
            else:
                legal = Legals.getLegaldata(xml_participant.get('inn'), xml_participant.get('ogrn'),
                                            xml_participant.get('orgname'), xml_participant.get('kpp'), "individual",
                                            xml_participant['xpath'], db_logger, self.filename)
            print("legal: %s" % legal._id)
            participant = Participants.saveParticipant(notification, legal._id,
                                                        self.publishdate, xml_participant.get('app_date'),
                                                       xml_participant.get('journal_number'),
                                                       xml_participant.get('appratting'),
                                                       xml_participant.get('admitted'),
                                                       xml_participant.get('offer_date'),
                                                       xml_participant.get('offer_price'), protocol)

        elif not xml_participant['inn'] and (
                        xml_participant['participant_type'] == 'UF' or xml_participant['id_number']):
            legal = Legals.getLegaldata(None, None,
                                        xml_participant.get('orgname'), None, "foreign",
                                        xml_participant['xpath'], db_logger, self.filename)
            print("legal: %s" % legal._id)
            participant = Participants.saveParticipant(notification, legal._id,
                                                        self.publishdate,
                                                       xml_participant.get('app_date'),
                                                       xml_participant.get('journal_number'),
                                                       xml_participant.get('appratting'),
                                                       xml_participant.get('admitted'),
                                                       xml_participant.get('offer_date'),
                                                       xml_participant.get('offer_price'), protocol)

        if participant:
            print("Participant: %s" % participant.application_number)
        return participant

    def add_winner(self, participant, protocol, db_logger, xpath):
        winner = Winners.saveWinnerData(participant._legal, participant._notification,
                                        protocol, participant.offer_date,
                                        participant.offer_price, participant._actuality,
                                        xpath, db_logger, self.filename)

        print("Winner: %s" % winner._id)

    def put_cancel_protocol(self):
        logname = 'Protocol_loader' + self.filename
        print(self.filename)
        db_logger = LoggerDb(log_name=logname, log_file=PROTOCOL_LOG_FILE, job='protocols')
        # Get Notification data
        notification_data = Notifications.select().where(Notifications.regnumber == self.purchasenumber)
        for notification in notification_data:
            print("Notification: %s" % notification._id)
            # Get Protocol data
            protocol = Protocols.getProtocol(notification._id, self.protocolnum, self.docpublishdate,
                                     self.protocol_date, self.sign_date,
                                     self.protocolnum_xpath, db_logger, self.filename, self.protocol_type)
            if protocol:
                print("Protocol: %s , %s" % (protocol._id, protocol.publish_date))
                winner = Winners.saveWinnerData(None, notification._id, protocol._id, None, None, None,
                                            self.protocolnum_xpath, db_logger, self.filename, cancel=True)



    def put_evasion_protocol(self):
        logname = 'Protocol_loader' + self.filename
        print(self.filename)
        db_logger = LoggerDb(log_name=logname, log_file=PROTOCOL_LOG_FILE, job='protocols')
        # Get Notification data
        for lot in self.lot_data:
            notification = Notifications.get_or_create(regnumber=self.purchasenumber, lotnumber=self.lotnumber,
                                                       law='44')
            if notification[1]:
                print('INSERT')
                db_logger.write_log('INSERT', 'public.notifications', notification[0]._id, self.filename, self.purchasenumber_xpath)
            print("Notification: %s" % notification[0]._id)
            # Get Protocol data
            protocol = Protocols.getProtocol(notification[0]._id, self.protocolnum, self.docpublishdate,
                                             self.protocol_date, self.sign_date,
                                             self.protocolnum_xpath, db_logger, self.filename, self.protocol_type)
            for xml_participant in self.lot_data.get(lot):
                participant = Participants.get_participant(notification[0]._id,
                                                    xml_participant['journal_number'])

                if participant:
                    Winners.winner_evasion(participant, protocol._id, self.filename, self.protocolnum_xpath, db_logger)


class ProtocolOkParser(ProtocolParser):
    "Обработчик для протоколов открытого аукциона"
    def getLotData(self):
        self.lot_data = {}
        if self.protocol_type == 'fcsProtocolCancel':
            self.put_cancel_protocol()
        for lot in self.protocol_lots:
            self.lotnumber = \
                ParsingTools.get_val_from_node(lot.xpath("./export:lotNumber", namespaces=self.nsmp)) or 1
            print(self.lotnumber)
            self.is_abandoned = False if len(lot.xpath("./export:abandonedReason", namespaces=self.nsmp)) == 0 else True
            if self.protocol_type == 'fcsProtocolOKSingleApp':
                self.participants = lot.xpath("./export:application", namespaces=self.nsmp)
            else:
                self.participants = lot.xpath("./export:applications/export:application", namespaces=self.nsmp)
            self.participants_list = []
            for participant in self.participants:
                participant_dict = {}
                participant_dict['xpath'] = self.tree.getpath(participant)
                participant_dict['journal_number'] = ParsingTools.get_val_from_node(participant.xpath(
                                                                                             "./export:journalNumber",
                                                                                             namespaces=self.nsmp))
                participant_dict['app_date'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:appDate", namespaces=self.nsmp), is_date=True)
                participant_dict['offer_date'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:appDate", namespaces=self.nsmp), is_date=True)
                # Поиск предлженной цены в разных нодах
                participant_dict['offer_price0'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:offerPrice", namespaces=self.nsmp), is_num=True)
                criterions = participant.xpath(
                    "./export:contractConditions/export:contractCondition", namespaces=self.nsmp)
                participant_dict['offer_price1'] = None
                for price_criterion in criterions:
                    criterion_code = ParsingTools.get_val_from_node(price_criterion.xpath('./export:criterionCode',
                                                                                          namespaces=self.nsmp))
                    if criterion_code == 'CP':
                        participant_dict['offer_price1'] = ParsingTools.get_val_from_node(price_criterion.xpath(
                    "./export:offer", namespaces=self.nsmp), is_num=True)
                cost_criterions = participant.xpath(
                    "./export:admittedInfo/export:conditionsScoring/export:conditionScoring/export:costCriterion",
                    namespaces=self.nsmp)
                participant_dict['offer_price2'] = None
                for cost_criteria in cost_criterions:
                    cost_criterion_code = ParsingTools.get_val_from_node(cost_criteria.xpath('./export:criterionCode',
                                                                                          namespaces=self.nsmp))
                    if cost_criterion_code == 'CP':
                        participant_dict['offer_price2'] = ParsingTools.get_val_from_node(cost_criteria.xpath(
                                                                                                   "./export:offer",
                                                                                                   namespaces=self.nsmp),
                            is_num=True)
                participant_dict['offer_price3'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:price", namespaces=self.nsmp), is_num=True)
                participant_dict['admitted'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:admittedInfo/export:admitted", namespaces=self.nsmp), is_bool=True)
                participant_dict['appratting'] = ParsingTools.get_val_from_node(participant.xpath(
                    "./export:admittedInfo/export:appRating", namespaces=self.nsmp))
                app_participants = participant.xpath("./export:appParticipants/export:appParticipant", namespaces=self.nsmp)
                app_participant_data = []
                for app_participant in app_participants:
                    app_participant_dict = {}
                    app_participant_dict['participant_type'] = ParsingTools.get_val_from_node(app_participant.xpath(
                                                                                                   "./export:participantType",
                                                                                                   namespaces=self.nsmp))
                    app_participant_dict['inn'] = ParsingTools.check_inn(ParsingTools.get_val_from_node(app_participant.xpath(
                                                                                                             "./export:inn",
                                                                                                             namespaces=self.nsmp)))
                    app_participant_dict['kpp'] = ParsingTools.check_kpp(ParsingTools.get_val_from_node(app_participant.xpath(
                                                                                                             "./export:kpp",
                                                                                                             namespaces=self.nsmp)))
                    app_participant_dict['ogrn'] = ParsingTools.check_ogrn(ParsingTools.get_val_from_node(app_participant.xpath(
                                                                                                               "./export:ogrn",
                                                                                                               namespaces=self.nsmp)))
                    app_participant_dict['id_number'] = ParsingTools.get_val_from_node(app_participant.xpath(
                                                                                            "./export:idNumber",
                                                                                            namespaces=self.nsmp))
                    app_participant_dict['orgname'] = ParsingTools.get_val_from_node(app_participant.xpath(
                        "./export:organizationName", namespaces=self.nsmp))
                    app_participant_dict['firmname'] = ParsingTools.get_val_from_node(app_participant.xpath(
                                                                                           "./export:firmName",
                                                                                           namespaces=self.nsmp))
                    app_participant_dict['lastname'] = ParsingTools.get_val_from_node(app_participant.xpath(
                                                                                           "./export:contactInfo/export:lastName",
                                                                                           namespaces=self.nsmp))
                    app_participant_dict['firstname'] = ParsingTools.get_val_from_node(app_participant.xpath(
                                                                                            "./export:contactInfo/export:firstName",
                                                                                            namespaces=self.nsmp))
                    app_participant_dict['middlename'] = ParsingTools.get_val_from_node(app_participant.xpath(
                                                                                             "./export:contactInfo/export:middleName",
                                                                                             namespaces=self.nsmp))
                    app_participant_data.append(app_participant_dict)

                participant_dict['app_participant_data'] = app_participant_data
                self.participants_list.append(participant_dict)

            self.lot_data.update({self.lotnumber: self.participants_list})
        self.putXmlDataToDb()

    def putXmlDataToDb(self):
        "Загрузка данных из xml протокола открытого конкурса в базу данных"
        logname = 'Protocol_loader' + self.filename
        db_logger = LoggerDb(log_name=logname, log_file=PROTOCOL_LOG_FILE, job='Protocol')
        for lot in self.lot_data.keys():
            # Get Notification data
            notification = Notifications.get_or_create(regnumber=self.purchasenumber, lotnumber=lot, law='44')
            if notification[1]:
                print('INSERT')
                db_logger.write_log('INSERT', 'public.notifications', notification[0]._id, self.filename, self.purchasenumber_xpath)
            print("Notification: %s" % notification[0]._id)
            # Get Protocol data
            protocol = Protocols.getProtocol(notification[0]._id, self.protocolnum_xpath, self.publishdate,
                                             self.protocol_date, self.sign_date,
                                             self.protocolnum_xpath, db_logger, self.filename, self.protocol_type,
                                             self.is_abandoned)
            if protocol:
                print("Protocol: %s , %s" % (protocol._id, protocol.publish_date))
                print("Publishdate = ", self.publishdate)

            for xml_participant in self.lot_data.get(lot):
                if len(xml_participant.get('app_participant_data'))>1:
                    db_logger.write_warning('More then 1 participant for application!')

                for legal_data in xml_participant.get('app_participant_data'):
                    xml_participant['inn'] = legal_data['inn']
                    xml_participant['ogrn'] = legal_data['ogrn']
                    xml_participant['id_number'] = legal_data['id_number']
                    xml_participant['kpp'] = legal_data['kpp']
                    xml_participant['orgname'] = legal_data['orgname']
                    xml_participant['participant_type'] = legal_data['participant_type']
                    xml_participant['firmname'] = legal_data['firmname']
                    xml_participant['lastname'] = legal_data['lastname']
                    xml_participant['firstname'] = legal_data['firstname']
                    xml_participant['middlename'] = legal_data['middlename']
                    break
                xml_participant['offer_price'] = None
                for offer_data in (xml_participant['offer_price0'], xml_participant['offer_price1'],
                                   xml_participant['offer_price2'],xml_participant['offer_price3']):
                    if offer_data:
                        xml_participant['offer_price'] = offer_data
                        break
                if xml_participant['offer_price']:
                    print('offer_price = ', xml_participant['offer_price'])
                participant = self.add_participant_with_legal(notification[0]._id, xml_participant, db_logger,  protocol._id)
                # is winner
                if participant and (xml_participant['admitted'] or xml_participant['appratting'] == '1'):
                    self.add_winner(participant, protocol._id, db_logger,
                                    xml_participant.get('xpath'))
        db_logger.close_log()

class ProtocolZKParser(ProtocolParser):
    def putXmlDataToDb(self):
        logname = 'Protocol_loader' + self.filename
        print(self.filename)
        db_logger = LoggerDb(log_name=logname, log_file=PROTOCOL_LOG_FILE, job='protocols')
        for lot in self.lot_data:
            # Get Notification data
            notification = Notifications.get_or_create(regnumber=self.purchasenumber, lotnumber=self.lotnumber, law='44')
            if notification[1]:
                print('INSERT')
                db_logger.write_log('INSERT', 'public.notifications', notification[0]._id, self.filename, self.purchasenumber_xpath)
            print("Notification: %s" % notification[0]._id)
            # Get Protocol data
            protocol = Protocols.getProtocol(notification[0]._id, self.protocolnum, self.publishdate,
                                             self.protocol_date, self.sign_date,
                                             self.protocolnum_xpath, db_logger, self.filename, self.protocol_type,
                                             self.is_abandoned)
            if protocol:
                print("Protocol: %s , %s" % (protocol._id, protocol.publish_date))
                print("Publishdate = ", self.publishdate)


            for xml_participant in self.lot_data.get(lot):
                xml_participant['offer_price'] = xml_participant['offer_price_zk']
                xml_participant['offer_date'] = xml_participant['app_date']
                participant = self.add_participant_with_legal(notification[0]._id, xml_participant, db_logger,  protocol._id)
                # is winner
                if participant and xml_participant['admitted_result'] in ['WIN_OFFER', 'ADMITTED_OFFER']:
                    self.add_winner(participant, protocol._id, db_logger,
                                    xml_participant['xpath'])


        print("-----------------------------------------------------------------------------------------End of work")
        db_logger.close_log()


class ProtocolZPParser(ProtocolParser):
    def putXmlDataToDb(self):
        logname = 'Protocol_loader' + self.filename
        print(self.filename)
        db_logger = LoggerDb(log_name=logname, log_file=PROTOCOL_LOG_FILE, job='protocols')
        for lot in self.lot_data:
            # Get Notification data
            notification = Notifications.get_or_create(regnumber=self.purchasenumber, lotnumber=self.lotnumber, law='44')
            if notification[1]:
                print('INSERT')
                db_logger.write_log('INSERT', 'public.notifications', notification[0]._id, self.filename, self.purchasenumber_xpath)
            print("Notification: %s" % notification[0]._id)
            # Get Protocol data
            protocol = Protocols.getProtocol(notification[0]._id, self.protocolnum, self.publishdate,
                                             self.protocol_date, self.sign_date,
                                             self.protocolnum_xpath, db_logger, self.filename, self.protocol_type,
                                             self.is_abandoned)
            if protocol:
                print("Protocol: %s , %s" % (protocol._id, protocol.publish_date))
                print("Publishdate = ", self.publishdate)

            for xml_participant in self.lot_data.get(lot):
                if xml_participant['offer_price_zp']:
                    xml_participant['offer_price'] = xml_participant['offer_price_zp']
                else:
                    xml_participant['offer_price'] = xml_participant['offer_price_zk']
                if xml_participant['offer_date_zp']:
                    xml_participant['offer_date'] = xml_participant['offer_date_zp']
                else:
                    xml_participant['offer_date'] = xml_participant['app_date']

                participant = self.add_participant_with_legal(notification[0]._id, xml_participant, db_logger,  protocol._id)
                # is winner
                if participant and xml_participant['appratting'] == '1':
                    self.add_winner(participant, protocol._id, db_logger,
                                    xml_participant['xpath'])


        print("-----------------------------------------------------------------------------------------End of work")
        db_logger.close_log()


class ProtocolPOParser(ProtocolParser):
    def putXmlDataToDb(self):
        logname = 'Protocol_loader' + self.filename
        print(self.filename)
        db_logger = LoggerDb(log_name=logname, log_file=PROTOCOL_LOG_FILE, job='protocols')
        for lot in self.lot_data:
            # Get Notification data
            notification = Notifications.get_or_create(regnumber=self.purchasenumber,
                                                       lotnumber=self.lotnumber, law='44')
            if notification[1]:
                print('INSERT')
                db_logger.write_log('INSERT', 'public.notifications', notification[0]._id, self.filename,
                                    self.purchasenumber_xpath)
            print("Notification: %s" % notification[0]._id)
            # Get Protocol data
            protocol = Protocols.getProtocol(notification[0]._id, self.protocolnum, self.publishdate,
                                             self.protocol_date, self.sign_date,
                                             self.protocolnum_xpath, db_logger, self.filename, self.protocol_type,
                                             self.is_abandoned)
            if protocol:
                print("Protocol: %s , %s" % (protocol._id, protocol.publish_date))
                print("Publishdate = ", self.publishdate)

            for xml_participant in self.lot_data.get(lot):
                xml_participant['admitted'] = xml_participant['included']

                participant = self.add_participant_with_legal(notification[0]._id, xml_participant, db_logger,
                                                              protocol._id)


if __name__ == '__main__':
    protocol0 = ProtocolZKParser('C:\\Test.Zakupki.local\\fcs_regions\\Adygeja_Resp\protocols\\fcsProtocolZKBI_9911111111315000003_3220984.xml')
    #protocol1 = ProtocolOkParser('C:\\Test.Zakupki.local\\fcs_regions\\Adygeja_Resp\\protocols\\fcsProtocolPRE_0176200005514000057_1729150.xml')
    if protocol0.file_is_empty:
        print("FILE IS EMPTY")
