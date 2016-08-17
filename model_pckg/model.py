from peewee import Field, Model, DateField, CharField, BigIntegerField, ForeignKeyField, DateTimeField,\
    IntegerField, TextField, FloatField, CompositeKey, BooleanField, fn, JOIN_INNER
from playhouse.postgres_ext import BinaryJSONField
from model_pckg import DATABASE
import json

from xml_parsers.parsing_tools import ParsingTools

database = DATABASE


class LegalType(Field):
    db_field = 'legal_type'

    def db_value(self, value):
        return value

    def python_value(self, value):
        if value in ('individual', 'legal', 'goverment', 'state', 'pif', 'foreign', None):
            return value
        else:
            print('Invalid value for legal_type Field')


class BankStatus(Field):
    db_field = 'banks_status'


class OperationType(Field):
    db_field = 'operation_type'


class LawType(Field):
    db_field = 'law_type'


class NotificationStatus(Field):
    db_field = 'notifications_status'


class EnforcementType(Field):
    db_field = 'enforcement_type'


class ContractStage(Field):
    db_field = 'contract_stage'


class GuaranteeStatus(Field):
    db_field = 'guarantee_status'


class GuaranteeEnsure(Field):
    db_field = 'guarantee_ensure'


class ProtocolStatus(Field):
    db_field = 'protocol_status'


class RnpState(Field):
    db_field = 'rnp_state'


class CreateReason(Field):
    db_field = 'rnp_create_reason'

for field in ('banks_status', 'operation_type', 'operation_type', 'law_type', 'notifications_status',
              'enforcement_type', 'contract_stage', 'guarantee_status', 'guarantee_ensure', 'protocol_status',
              'rnp_state', 'rnp_create_reason'):
    dic = dict(field=field)
    database.register_fields(dic)


class BaseModel(Model):
    class Meta:
        database = database


class Legals(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _parent = BigIntegerField(db_column='__parent_id', index=True, null=True)
    capital = BigIntegerField(null=True)
    firstname = CharField(index=True, null=True)
    fulltitle = CharField(index=True, null=True)
    inn = CharField(index=True, null=True)
    kpp = CharField(null=True)
    lastname = CharField(index=True, null=True)
    middlename = CharField(index=True, null=True)
    ogrn = CharField(null=True, unique=True)
    ogrn_date = DateField(null=True)
    okopf_code = CharField(null=True)
    region_code = CharField(null=True)
    region_name = CharField(null=True)
    shorttitle = CharField(null=True)
    type = LegalType(index=True, null=True)  # USER-DEFINED
    name = CharField(null=True)

    class Meta:
        db_table = 'legals'
        indexes = (
            (('__parent', 'inn'), True),
        )
        schema = 'public'


    @staticmethod
    def getLegaldata(inn, ogrn, orgname, kpp, type, xpath, logger, filename, lastname=None, firstname=None,
                     middlename=None):
        try:
            if not inn and not ogrn:
                legal = Legals.select(Legals._id).where(Legals.fulltitle == orgname).get()

            elif ogrn:
                legal = Legals.select(Legals._id, Legals.kpp).where(
                    ((Legals.ogrn == ogrn) & (Legals._parent == None))).get()

            else:
                legal = Legals.select(Legals._id, Legals.kpp).where(
                    ((Legals.inn == inn) & (Legals._parent == None))).get()

            if legal.kpp is not None and kpp is not None and legal.kpp != kpp:
                try:
                    return Legals.select(Legals._id).where((Legals.inn == inn) & (Legals.kpp == kpp) & ~(Legals._parent == None)).get()
                except Legals.DoesNotExist:
                    return Legals.create(_parent=legal._id, inn=inn, ogrn=ogrn, fulltitle=orgname,
                                     kpp=kpp, name=orgname)
            else:
                return legal
        except Legals.DoesNotExist:
            if lastname:

                legal = Legals.create(inn=inn, ogrn=ogrn, lastname=ParsingTools.person_name(lastname),
                                      firstname=ParsingTools.person_name(firstname),
                                      middlename=ParsingTools.person_name(middlename),
                                      type=type, name='%s %s %s' % (lastname, firstname if firstname else '',
                                                                    middlename if middlename else ''))
            else:
                legal = Legals.create(inn=inn, ogrn=ogrn,
                                        fulltitle=orgname,
                                        kpp=kpp,
                                        type=type,name=orgname)
                logger.write_log('INSERT', 'public.legals', legal._id, filename, xpath)

            return legal

    @staticmethod
    def put_egrul_data(inn, ogrn, kpp, fulltitle, capital, okopf_code, ogrn_date, type, actuality, logger, xpath,
                       filename, shorttitle=None, parent=None, region_code=None, region_name=None):
        name = shorttitle or fulltitle
        try:
            if not inn and not ogrn:
                legal_db = Legals.select().where(Legals.fulltitle == fulltitle).get()

            elif ogrn:
                legal_db = Legals.select().where(
                    ((Legals.ogrn == ogrn) & (Legals._parent == None))).get()

            else:
                legal_db = Legals.select().where(
                    ((Legals.inn == inn) & (Legals._parent == None))).get()

            legal_f = Legals(inn=inn, ogrn=ogrn, kpp=kpp, fulltitle=fulltitle, capital=capital, okopf_code=okopf_code,
                             ogrn_date=ogrn_date, type=type, shorttitle=shorttitle, _parent=parent, _actuality=actuality,
                             region_code=region_code, region_name=region_name, name=name)
            legal_final = ParsingTools.compare_two_inst(legal_db, legal_db.__dict__['_data'], legal_f.__dict__['_data'])
            r = legal_final.save()
            if r:
                logger.write_log('UPDATE', 'public.legals', legal_final._id, filename, xpath)
        except Legals.DoesNotExist:
            legal_final = Legals.create(inn=inn, ogrn=ogrn, kpp=kpp, fulltitle=fulltitle, capital=capital,
                                        okopf_code=okopf_code,ogrn_date=ogrn_date, type=type, shorttitle=shorttitle,
                                        _parent=parent, _actuality=actuality,region_code=region_code,
                                        region_name=region_name, name=name)
            logger.write_log('INSERT', 'public.legals', legal_final._id, filename, xpath)
        return legal_final


class Banks(BaseModel):
    _actuality = DateTimeField(null=True, db_column='__actuality')
    _created = DateTimeField(db_column='__created')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _legal = ForeignKeyField(db_column='__legal_id', null=True, rel_model=Legals, to_field='_id')
    _updated = DateTimeField()
    bic = CharField(null=True, unique=True)
    registration_date = DateField(null=True)
    regnumber = IntegerField(null=True, unique=True)
    status = BankStatus(index=True, null=True)  # USER-DEFINED
    ustmoney = BigIntegerField(null=True)

    class Meta:
        db_table = 'banks'
        schema = 'public'


class RegistryCustomers(BaseModel):
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _legal = ForeignKeyField(db_column='__legal_id', null=True, rel_model=Legals, to_field='_id', unique=True)
    regnumber_223 = CharField(null=True, unique=True)
    regnumber_44 = CharField(null=True, unique=True)

    class Meta:
        db_table = 'registry_customers'
        schema = 'public'

    @staticmethod
    def get_customer_data(regnumber, law):
        try:
            if regnumber:
                if law != '223':
                    customer = RegistryCustomers.select().where(RegistryCustomers.regnumber_44 == regnumber).get()
                    return customer
                else:
                    customer = RegistryCustomers.select().where(RegistryCustomers.regnumber_223 == regnumber).get()
                    return customer
            else:
                raise RegistryCustomers.DoesNotExist
        except RegistryCustomers.DoesNotExist:
            return RegistryCustomers()




class Etp(BaseModel):
    _actuality = DateTimeField(null=True, db_column='__actuality')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    code = CharField(null=True)
    name = CharField(null=True)

    class Meta:
        db_table = 'etp'
        schema = 'public'


class Notifications(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _created = DateTimeField(index=True, db_column='__created')
    _etp_id = ForeignKeyField(db_column='__etp_id', null=True, rel_model=Etp, to_field='_id')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _updated = DateTimeField(index=True, db_column='__updated')
    collecting_date = DateField(index=True, null=True)
    contract_guarantee_amount = BigIntegerField(null=True)
    currency = CharField(null=True)
    law = LawType(null=True)  # USER-DEFINED
    lotnumber = IntegerField(null=True)
    maxprice = BigIntegerField(null=True)
    placingway_code = CharField(index=True, null=True)
    publish_date = DateField(index=True, null=True)
    purchase_guarantee_amount = BigIntegerField(null=True)
    purchase_title = TextField(null=True)
    regnumber = CharField(null=True)
    scoring_date = DateField(index=True, null=True)
    status = NotificationStatus(null=True)  # USER-DEFINED

    class Meta:
        db_table = 'notifications'
        indexes = (
            (('lotnumber', 'regnumber'), True),
        )
        schema = 'public'

    @staticmethod
    def get_notification_data(regnum, lot, law, logger, xpath, filename):
        try:
            notification_db = Notifications.select().where(Notifications.regnumber == regnum, Notifications.lotnumber == lot).get()
            notification_f = Notifications(regnumber=regnum, lotnumber=lot, law=law)

            pdb_attrs = vars(notification_db)
            pfl_attrs = vars(notification_f)

            notification = ParsingTools.compare_two_inst(notification_db, pdb_attrs['_data'],
                                                         pfl_attrs['_data'])
            r = notification.save()
            if r:
                logger.write_log('UPDATE', 'public.notification', notification._id, filename, xpath)
        except Notifications.DoesNotExist:
            notification = Notifications.create(regnumber=regnum, lotnumber=lot, law=law)
            logger.write_log('INSERT', 'public.notification', notification._id, filename, xpath)
        return notification


class Protocols(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _notification = ForeignKeyField(db_column='__notification_id', rel_model=Notifications, to_field='_id', unique=True)
    protocol_date = DateField(index=True, null=True)
    protocolnumber = CharField(null=True)
    publish_date = DateField(index=True, null=True)
    sign_date = DateField(index=True, null=True)
    status = ProtocolStatus(null=True)

    class Meta:
        db_table = 'protocols'
        schema = 'public'

    @staticmethod
    def getProtocol(notification, protocol, publishdate, protocol_date, sign_date, xpath, logger, filename, protocol_type,
                    is_abandoned=False):
        status = None
        if 'EF' in protocol_type or protocol_type in ['fcsProtocolCancel', 'fcsProtocolEvasion']:
            if 'EF1' in protocol_type or 'EF2' in protocol_type:
                status = 'processing'
            elif protocol_type == 'fcsProtocolCancel':
                status = 'cancelled'
            elif protocol_type == 'fcsProtocolEvasion':
                status = 'evasion'
            elif protocol_type == 'fcsProtocolEFInvalidation':
                status = 'invalidated'
            else:
                status = 'finished'
        elif 'OK' in protocol_type:
            if is_abandoned:
                status = 'invalidated'
            else:
                for ext in ['OK2', 'OKD5', 'OKOU3', 'SingleApp']:
                    if ext in protocol_type:
                        status = 'finished'
                        break
                else:
                    status = 'processing'
        elif 'ZK' in protocol_type:
            if is_abandoned:
                status = 'invalidated'
            else:
                status = 'finished'
        elif 'ZP' in protocol_type:
            if is_abandoned:
                status = 'invalidated'
            elif 'Extract' in protocol_type:
                status = 'processing'
            else:
                status = 'finished'

        try:
            if protocol_type == 'fcsProtocolCancel':
                try:
                    protocol_db = Protocols.select().where(Protocols._notification == notification, Protocols.protocolnumber == protocol).get()
                except Protocols.DoesNotExist:
                    return None
            else:
                protocol_db = Protocols.select().where(Protocols._notification == notification,
                                                       Protocols.protocolnumber == protocol).get()


            protocol_from_file = Protocols(_actuality=publishdate, protocolnumber=protocol,
                                           _notification=notification,
                                           protocol_date=protocol_date, sign_date=sign_date,
                                           publish_date=publishdate, status=status)

            pdb_attrs = vars(protocol_db)
            pfl_attrs = vars(protocol_from_file)

            protocol_final = ParsingTools.compare_two_inst(protocol_db, pdb_attrs['_data'], pfl_attrs['_data'])
            r = protocol_final.save()
            if r:
               logger.write_log('UPDATE', 'public.protocols', protocol_final._id, filename, xpath)
        except Protocols.DoesNotExist:
            protocol_final = Protocols.create(_notification=notification, protocolnumber=protocol,
                                              publish_date=publishdate, protocol_date=protocol_date,
                                              sign_date=sign_date, _actuality=publishdate, status=status)
            logger.write_log('INSERT', 'public.protocols', protocol_final._id, filename, xpath)

        return protocol_final


class Winners(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _legal = ForeignKeyField(db_column='__legal_id', rel_model=Legals, to_field='_id')
    _notification = ForeignKeyField(db_column='__notification_id', rel_model=Notifications, to_field='_id')
    _protocol = ForeignKeyField(db_column='__protocol_id', rel_model=Protocols, to_field='_id')
    offer_date = DateField(index=True, null=True)
    offer_price = BigIntegerField(null=True)
    wins = BooleanField(null=True)

    class Meta:
        db_table = 'winners'
        indexes = (
            (('__notification', '__protocol'), True),
        )
        schema = 'public'

    @staticmethod
    def saveWinnerData(legal, notification, protocol, offer_date, offer_price, _actuality, xpath, logger, filename,
                       cancel=False):
        try:
            if cancel:
                try:
                    winner_final = Winners.select().where(Winners._notification == notification,
                                                          Winners._protocol == protocol).get()
                    winner_final.wins = False
                    winner_final.save()
                    logger.write_log('UPDATE', 'public.winners', winner_final._id, filename, xpath)
                    winner_final.delete_instance()
                    logger.write_log('DELETE', 'public.winners', winner_final._id, filename, xpath)
                except Winners.DoesNotExist:
                    return None
            else:
                winner_db = Winners.select().where(Winners._notification == notification).get()

                winner_f = Winners(_legal=legal, _notification=notification, _protocol=protocol,
                                   offer_date=offer_date, offer_price=offer_price,
                                   _actuality=_actuality)

                if winner_db._protocol!=winner_f._protocol:
                    winner_db.wins = False
                    winner_db.save()
                    logger.write_log('UPDATE', 'public.winners', winner_db._id, filename, xpath)
                    winner_db.delete_instance()
                    logger.write_log('DELETE', 'public.winners', winner_db._id, filename, xpath)
                    raise Winners.DoesNotExist
                else:
                    pdb_attrs=vars(winner_db)
                    pfl_attrs=vars(winner_f)

                    winner_final = ParsingTools.compare_two_inst(winner_db, pdb_attrs['_data'], pfl_attrs['_data'])
                    r = winner_final.save()
                    if r == 1:
                        logger.write_log('UPDATE', 'public.winners', winner_final._id, filename, xpath)
        except Winners.DoesNotExist:
            winner_final = Winners.create(_legal=legal, _notification=notification, _protocol=protocol,
                               offer_date=offer_date, offer_price=offer_price,_actuality=_actuality, wins=True)
            logger.write_log('INSERT', 'public.winners', winner_final._id, filename, xpath)

        return winner_final
    @staticmethod
    def winner_evasion(participant, protocol_id, filename, xpath, logger):
        try:
            winner = Winners.select().where(Winners._notification == participant._notification).get()
            if winner._legal == participant._legal:
                winner.wins = False
                winner._protocol = protocol_id
                winner.save()
                logger.write_log('UPDATE', 'public.winners', winner._id, filename, xpath)
                winner.delete_instance()
                logger.write_log('DELETE', 'public.winners', winner._id, filename, xpath)
        except Winners.DoesNotExist:
            logger.write_warning("GOT contract-evasion protocol, but  no winner to update")


class Customers(BaseModel):
    _id = BigIntegerField(primary_key=True, db_column='__id')
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _legal = ForeignKeyField(db_column='__legal_id', rel_model=Legals, to_field='_id')
    _notification = ForeignKeyField(db_column='__notification_id', rel_model=Notifications, to_field='_id')
    contract_guarantee_amount = BigIntegerField(null=True)
    contract_guarantee_part = FloatField(null=True)
    delivery_term = TextField(null=True)
    maxprice = BigIntegerField()
    purchase_guarantee_amount = BigIntegerField(null=True)
    purchase_guarantee_part = FloatField(null=True)

    class Meta:
        db_table = 'customers'
        indexes = (
            (('__notification', '__legal'), True),
        )
        schema = 'public'
    @staticmethod
    def get_customer_data(notification, customer, logger, xpath, filename, contract_regnum):
        try:
            if notification._id:
                customer_db = Customers.select(Customers._id).where(Customers._notification == notification._id,
                                                   Customers._legal == customer).get()

            else:
                customer_db = Customers.select(Customers._id).join(Contracts)\
                    .where(Customers._legal==customer, Contracts.regnumber==contract_regnum).get()
                #raise Customers.DoesNotExist
        except Customers.DoesNotExist:
            customer_db = Customers.create(_legal=customer, _notification=notification._id)
            logger.write_log('INSERT', 'public.customers', customer_db._id, filename, xpath)
        return customer_db



class Contracts(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _customer = ForeignKeyField(db_column='__customer_id', rel_model=Customers, to_field='_id')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    currency = CharField(null=True)
    end_date = DateField(index=True, null=True)
    enforcement = EnforcementType(null=True)  # USER-DEFINED
    enforcement_amount = BigIntegerField(null=True)
    enforcement_currency = CharField(null=True)
    price = BigIntegerField(null=True)
    price_rub=BigIntegerField(null=True)
    publish_date = DateField(index=True)
    regnumber = CharField(null=True)
    sign_date = DateField(index=True)
    stage = ContractStage(null=True)  # USER-DEFINED
    supplier = ForeignKeyField(db_column='supplier_id', rel_model=Legals, to_field="_id")
    _notification = ForeignKeyField(db_column='__notification_id', rel_model=Notifications, to_field='_id')
    law = LawType(null=True)

    class Meta:
        db_table = 'contracts'
        indexes = (
            (('__customer', '__winner'), True),
        )
        schema = 'public'
    @staticmethod
    def get_contract_data(notification, customer, regnumber, publishdate, signdate, enddate, price, price_rur, currency,
                          stage, enforcement, enforce_amount, enforce_curr, supplier, logger, filename, xpath, law):
        if stage == 'E':
            stage_enum = 'executed'
        elif stage == 'EC':
            stage_enum = 'completed'
        elif stage == 'ET':
            stage_enum = 'terminated'
        elif stage == 'IN':
            stage_enum = 'annulled'
        else:
            stage_enum = None

        try:
            contract_db = Contracts.select().where(Contracts.regnumber == regnumber).get()
            contract_fl = Contracts(_notification=notification, _customer=customer, regnumber=regnumber,
                                    publish_date=publishdate, sign_date=signdate, end_date=enddate,
                                    price=ParsingTools.currency_to_long(price, 100),
                                    price_rub=ParsingTools.currency_to_long(price_rur, 100),
                                    currency=currency, stage=stage_enum, supplier=supplier, enforcement=enforcement,
                                    enforcement_amount=ParsingTools.currency_to_long(enforce_amount, 100),
                                    enforcement_currency=enforce_curr, law=law, _actuality=publishdate)

            pdb_attrs = vars(contract_db)
            pfl_attrs = vars(contract_fl)

            contract_final = ParsingTools.compare_two_inst(contract_db, pdb_attrs['_data'], pfl_attrs['_data'])
            r = contract_final.save()
            if r == 1:
                logger.write_log('UPDATE', 'public.contracts', contract_final._id, filename, xpath)
        except Contracts.DoesNotExist:
            contract_final = Contracts.create(_notification=notification, _customer=customer, regnumber=regnumber,
                                    publish_date=publishdate, sign_date=signdate, end_date=enddate,
                                    price=ParsingTools.currency_to_long(price, 100),
                                    price_rub=ParsingTools.currency_to_long(price_rur, 100),
                                    currency=currency, stage=stage_enum, supplier=supplier, enforcement=enforcement,
                                    enforcement_amount=ParsingTools.currency_to_long(enforce_amount, 100),
                                    enforcement_currency=enforce_curr, _actuality=publishdate, law=law)
            logger.write_log('INSERT', 'public.contracts', contract_final._id, filename, xpath)
        return contract_final


class ContractsProducts(BaseModel):
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _contract = ForeignKeyField(db_column='__contract_id', rel_model=Contracts, to_field='_id')
    okpd = CharField(null=True)
    okpd2 = CharField(null=True)
    name = CharField(null=True)
    _actuality = DateTimeField(db_column='__actuality', null=True)

    class Meta:
        db_table = 'contracts_products'
        schema = 'public'

    @staticmethod
    def update_products(contract, okpd, okpd2, name, publishdate):
        prod_final = None
        name = name[:1024]
        try:
            if okpd:
                prod_db = ContractsProducts.select().where(ContractsProducts._contract == contract,
                                                           ContractsProducts.okpd == okpd).get()
            elif okpd2:
                prod_db = ContractsProducts.select().where(ContractsProducts._contract == contract,
                                                   ContractsProducts.okpd2 == okpd2).get()
            else:
                return prod_final

            prod_f = ContractsProducts(_contract=contract, okpd=okpd, okpd2=okpd2, name=name, _actuality=publishdate)

            pdb_attrs = vars(prod_db)
            pfl_attrs = vars(prod_f)

            prod_final = ParsingTools.compare_two_inst(prod_db, pdb_attrs['_data'], pfl_attrs['_data'])
            prod_final.save()
        except ContractsProducts.DoesNotExist:
            prod_final = ContractsProducts.create(_contract=contract, okpd=okpd, okpd2=okpd2, name=name,
                                                  _actuality=publishdate)

        return prod_final

class Contacts(BaseModel):
    _id = BigIntegerField(primary_key=True, db_column='__id')
    _contract = ForeignKeyField(rel_model=Contracts, db_column='__contract_id', to_field='_id')
    _legal = ForeignKeyField(db_column='__legal_id', rel_model=Legals, to_field='_id')
    data = BinaryJSONField()
    _actuality = DateTimeField(null=True, db_column='__actuality')

    class Meta:
        db_table = 'contacts'
        schema = 'public'

    @staticmethod
    def update_contact_data(contract, legal, contact_data, publishdate):
        try:
            contact_db = Contacts.select().where(Contacts._contract == contract, Contacts._legal == legal).get()

            pdb_attrs = contact_db.data
            pdb_attrs['contract'] = contact_db._contract
            pdb_attrs['legal'] = contact_db._legal
            pdb_attrs['actuality'] = contact_db._actuality

            pfl_attrs = contact_data
            pfl_attrs['contract'] = contract
            pfl_attrs['legal'] = legal
            pfl_attrs['actuality'] = publishdate

            contact_result = ParsingTools.compare_two_inst(None, pdb_attrs, pfl_attrs)

            contact_db._actuality = contact_result['actuality']

            contact_result.pop('contract')
            contact_result.pop('legal')
            contact_result.pop('actuality')

            contact_db.data = contact_result

            contact_db.save()
        except Contacts.DoesNotExist:
            contact_db = Contacts.create(_contract=contract, _legal=legal, data=contact_data, _actuality=publishdate)
        return contact_db


class EtpHistory(BaseModel):
    __id = BigIntegerField(db_column='__id')
    __operation = OperationType()  # USER-DEFINED
    code = CharField(null=True)
    name = CharField(null=True)

    class Meta:
        db_table = 'etp_history'
        schema = 'public'


class Guarantees(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _bank = ForeignKeyField(db_column='__bank_id', null=True, rel_model=Banks, to_field='_id')
    _created = DateTimeField(index=True, db_column='__created')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _updated = DateTimeField(index=True, db_column='__updated')
    amount = BigIntegerField(null=True)
    currency = CharField(null=True)
    ensure = GuaranteeEnsure(index=True, null=True)  # USER-DEFINED
    entryforce_date = DateField(index=True, null=True)
    expire_date = DateField(index=True, null=True)
    issue_date = DateField(index=True, null=True)
    publish_date = DateField(index=True, null=True)
    regnumber = CharField(null=True, unique=True)
    status = GuaranteeStatus(index=True, null=True)  # USER-DEFINED

    class Meta:
        db_table = 'guarantees'
        schema = 'public'


class LegalsAddresses(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _legal = ForeignKeyField(db_column='__legal_id', rel_model=Legals, to_field='_id', unique=True, primary_key=True)
    building = CharField(null=True)
    city_name = CharField(null=True)
    city_type = CharField(null=True)
    community_name = CharField(null=True)
    community_type = CharField(null=True)
    district_name = CharField(null=True)
    district_type = CharField(null=True)
    flat = CharField(null=True)
    house = CharField(null=True)
    kladr_code = CharField(null=True)
    postcode = CharField(null=True)
    region_code = CharField(index=True, null=True)
    region_name = CharField(null=True)
    region_type = CharField(null=True)
    street_name = CharField(null=True)
    street_type = CharField(null=True)

    class Meta:
        db_table = 'legals_addresses'
        schema = 'public'

    @staticmethod
    def update_address_data(legal, postcode, region_code, kladr_code, region_type, region_name, district_type, district_name,
                            city_type, city_name, community_type, community_name, street_type, street_name, house, building,
                            flat):
        try:
            addr_db = LegalsAddresses.select().where(LegalsAddresses._legal == legal).get()
            addr_f = LegalsAddresses(_legal=legal, postcode=postcode, region_code=region_code, kladr_code=kladr_code,
                                     region_type=region_type, region_name=region_name, district_type=district_type,
                                     district_name=district_name, city_type=city_type, city_name=city_name,
                                     community_type=community_type, community_name=community_name, street_type=street_type,
                                     street_name=street_name, house=house, building=building, flat=flat)
            addr_final = ParsingTools.compare_two_inst(addr_db, addr_db.__dict__['_data'], addr_f.__dict__['_data'])
            addr_final.save()
        except LegalsAddresses.DoesNotExist:
            addr_final = LegalsAddresses.create(_legal=legal, postcode=postcode, region_code=region_code, kladr_code=kladr_code,
                                     region_type=region_type, region_name=region_name, district_type=district_type,
                                     district_name=district_name, city_type=city_type, city_name=city_name,
                                     community_type=community_type, community_name=community_name, street_type=street_type,
                                     street_name=street_name, house=house, building=building, flat=flat)

        return addr_final

class Persons(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _created = DateTimeField(index=True, db_column='__created')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _updated = DateTimeField(index=True, db_column='__updated')
    firstname = CharField(index=True, null=True)
    inn = CharField(index=True, null=True)
    lastname = CharField(index=True, null=True)
    middlename = CharField(index=True, null=True)

    class Meta:
        db_table = 'persons'
        schema = 'public'


class LegalsFounders(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _created = DateTimeField(index=True, db_column='__created')
    _founder_legal = ForeignKeyField(db_column='__founder_legal_id', null=True, rel_model=Legals, to_field='_id')
    _founder_person = ForeignKeyField(db_column='__founder_person_id', null=True, rel_model=Persons, to_field='_id')
    _legal = ForeignKeyField(db_column='__legal_id', rel_model=Legals, related_name='legals___legal_set', to_field='_id')
    _updated = DateTimeField(index=True, db_column='__updated')
    part_amount = BigIntegerField(null=True)
    part_percent = FloatField(null=True)

    class Meta:
        db_table = 'legals_founders'
        schema = 'public'
        primary_key = CompositeKey('_legal', '_founder_person', '_founder_legal')


class LegalsHeads(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _created = DateTimeField(index=True, db_column='__created')
    _legal = ForeignKeyField(db_column='__legal_id', rel_model=Legals, to_field='_id')
    _person = ForeignKeyField(db_column='__person_id', rel_model=Persons, to_field='_id')
    _updated = DateTimeField(index=True, db_column='__updated')
    position_code = CharField(null=True)
    position_date = DateField()
    position_name = CharField(null=True)
    position_type = CharField(null=True)

    class Meta:
        db_table = 'legals_heads'
        indexes = (
            (('__person', '__legal'), True),
        )
        schema = 'public'
        primary_key = CompositeKey('_legal', '_person')


class Minfin(BaseModel):
    _actuality = DateTimeField(null=True, db_column='__actuality')
    _bank = ForeignKeyField(db_column='__bank_id', null=True, rel_model=Banks, to_field='_id')
    _created = DateTimeField(db_column='__created')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _updated = DateTimeField(db_column='__updated')
    listdate = DateTimeField(index=True, null=True)
    publishdate = DateTimeField(null=True)

    class Meta:
        db_table = 'minfin'
        indexes = (
            (('__bank', 'listdate'), True),
        )
        schema = 'public'


class Participants(BaseModel):
    _actuality = DateTimeField(index=True, null=True, db_column='__actuality')
    _legal = ForeignKeyField(db_column='__legal_id', null=True, rel_model=Legals, to_field='_id')
    _notification = ForeignKeyField(db_column='__notification_id', rel_model=Notifications, to_field='_id')
    application_date = DateField(index=True, null=True)
    application_number = CharField(null=True)
    application_rating = IntegerField(null=True)
    info = TextField(null=True)
    is_admitted = BooleanField(null=True)
    offer_date = DateField(null=True)
    offer_price = BigIntegerField(null=True)
    _protocol = ForeignKeyField(db_column='__protocol_id', rel_model=Protocols, to_field='_id')

    class Meta:
        db_table = 'participants'
        indexes = (
            (('__notification', '__legal'), True),
        )
        schema = 'public'
        primary_key = CompositeKey('application_number', '_notification')
    
    @staticmethod
    def saveParticipant(notification, legal, publishdate, app_date, journal_number, appratting, admitted,
                        offer_date,offer_price, protocol):
        try:
            participant_db = Participants.select().where(Participants._notification == notification,
                                                         Participants.application_number == journal_number).get()
            participant_f = Participants(_actuality=publishdate, _legal=legal, _notification=notification,
                                         application_date=app_date, application_number=journal_number,
                                         application_rating=appratting,is_admitted=admitted, offer_date=offer_date,
                                         offer_price=ParsingTools.currency_to_long(offer_price, 100), _protocol=protocol)

            pdb_attrs = vars(participant_db)
            pfl_attrs = vars(participant_f)

            participant = ParsingTools.compare_two_inst(participant_db, pdb_attrs['_data'], pfl_attrs['_data'])
            participant.save()
        except Participants.DoesNotExist:
            participant = Participants.create(_actuality=publishdate, _legal=legal, _notification=notification,
                                         application_date=app_date, application_number=journal_number,
                                         application_rating=appratting,is_admitted=admitted, offer_date=offer_date,
                                         offer_price=ParsingTools.currency_to_long(offer_price, 100), _protocol=protocol)
        return participant

    @staticmethod
    def get_participant(notification, journal_number):
        try:
            return Participants.select().where(Participants._notification == notification,
                                                      Participants.application_number == journal_number).get()
        except Participants.DoesNotExist:
            return None

class RegistryOkopf(BaseModel):
    _actuality = DateTimeField(null=True, db_column='__actuality')
    _created = DateTimeField(db_column='__created')
    _id = BigIntegerField(db_column='__id', primary_key=True)
    _parent = BigIntegerField(db_column='__parent_id', null=True)
    _updated = DateTimeField(db_column='__updated')
    actual = BooleanField(null=True)
    code = CharField(null=True, unique=True)
    fullname = CharField(null=True)
    legal_type = LegalType(null=True)  # USER-DEFINED
    singularname = CharField(null=True)

    class Meta:
        db_table = 'registry_okopf'
        schema = 'public'


class RegistrySsrf(BaseModel):
    id = BigIntegerField(db_column='__id', primary_key=True)
    code = CharField(null=True)
    name = CharField(null=True)
    actuality = DateTimeField(null=True, db_column='__actuality')

    class Meta:
        db_table = 'registry_ssrf'
        schema = 'public'


class RegistryRnp(BaseModel):
    id = BigIntegerField(db_column='__id', primary_key=True)
    regnumber = CharField(null=True)
    publish_date = DateField(null=True)
    approve_date = DateField(null=True)
    exclude_date = DateField(null=True)
    state = RnpState(null=True)
    create_reason = CreateReason(null=True)
    approve_reason = CharField(null=True)
    customer = ForeignKeyField(db_column='customer_id', rel_model=Legals, to_field='_id', related_name='customers')
    supplier = ForeignKeyField(db_column='supplier_id', rel_model=Legals, to_field='_id', related_name='suppliers')
    notification = ForeignKeyField(db_column='__notification_id', rel_model=Notifications, to_field='_id')
    contract = ForeignKeyField(db_column='__contract_id', rel_model=Contracts, to_field='_id')
    actuality = DateTimeField(null=True)

    class Meta:
        db_table = 'registry_rnp'
        schema = 'public'

