import re
import dbhelper
from trac.env import IEnvironmentSetupParticipant

class EstimatorSetupParticipant(Component):
    """ Makes sure our database is what we expect """
    implements(IEnvironmentSetupParticipant)
    dbversion = 1
    dbkey = 'EstimatorPluginDbVersion'
    def __init__(self):
        # Setup logging
        dbhelper.env = self.env
        dbhelper.mylog = self.log

    def environment_created(self):
        """Called when a new Trac environment is created."""
        if self.environment_needs_upgrade(None):
            self.upgrade_environment(None)

    def environment_needs_upgrade(self, db):
        """Called when Trac checks whether the environment needs to be upgraded.
        
        Should return `True` if this participant needs an upgrade to be
        performed, `False` otherwise.
        """
        ver = dbhelper.get_system_value(dbkey)
        return (not ver) or (ver < dbversion)

    def upgrade_environment(self, db):
        """Actually perform an environment upgrade.
        
        Implementations of this method should not commit any database
        transactions. This is done implicitly after all participants have
        performed the upgrades they need without an error being raised.
        """
        success = True
        if dbversion == 1:
            success &= dbhelper.execute_in_trans(
                ("""CREATE TABLE estimate(
                     id integer,
                     rate DECIMAL,
                     variability DECIMAL,
                     communication_overhead DECIMAL,
                     ticket_id integer
                 )""",),
                ("""CREATE TABLE estimate_line_item(
                     id integer,
                     estimate_id integer,
                     description VARCHAR(2048),
                     low_hours DECIMAL,
                     high_hours DECIMAL
                )""",))
        # SHOULD BE LAST IN THIS FUNCTION
        if success:
            dbhelper.set_system_value(dbkey, dbversion)
    
