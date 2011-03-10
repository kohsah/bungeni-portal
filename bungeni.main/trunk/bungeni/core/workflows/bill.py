import zope.securitypolicy.interfaces
from bungeni.core.workflows import utils
from bungeni.core.workflows import dbutils
from bungeni.models.utils import get_principal_id

class conditions(utils.conditions):
    pass

class actions(object):
    @staticmethod
    def create(info, context):
        utils.setParliamentId(info, context)
        user_id = get_principal_id()
        if not user_id:
            user_id = "-"
        zope.securitypolicy.interfaces.IPrincipalRoleMap(context
                        ).assignRoleToPrincipal("bungeni.Owner", user_id)
        owner_id = utils.getOwnerId(context)
        if owner_id and (owner_id != user_id):
            zope.securitypolicy.interfaces.IPrincipalRoleMap(context 
                ).assignRoleToPrincipal("bungeni.Owner", owner_id)
    
    @staticmethod
    def submit(info, context):
        utils.setBillPublicationDate(info, context)
        utils.createVersion(info, context)
        utils.setRegistryNumber(info, context)
    
    @staticmethod
    def withdraw(info, context):
        pass
    
    @staticmethod
    def schedule_first(info, context):
        pass
    
    @staticmethod
    def reschedule_first(info, context):
        pass
        
    @staticmethod
    def adjourn_first(info, context):
        pass


    @staticmethod
    def create_version(info, context):
        utils.createVersion(info, context)

    schedule_first_report_reading = create_version
    schedule_second_reading = create_version
