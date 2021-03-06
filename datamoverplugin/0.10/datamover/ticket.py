from trac.core import *
from trac.web.main import _open_environment
from trac.ticket.model import Component as TicketComponent, Ticket
from trac.ticket.query import Query

from webadmin.web_ui import IAdminPageProvider

from api import DatamoverSystem
from util import copy_ticket

class DatamoverTicketModule(Component):
    """The ticket moving component of the datamover plugin."""

    implements(IAdminPageProvider)
    
    # IAdminPageProvider methods
    def get_admin_pages(self, req):
        if req.perm.has_permission('TICKET_ADMIN'):
            yield ('mover', 'Data Mover', 'ticket', 'Tickets')
    
    def process_admin_request(self, req, cat, page, path_info):
        components = [c.name for c in TicketComponent.select(self.env)]
        envs = DatamoverSystem(self.env).all_environments()
        
        if req.method == 'POST':
            source_type = req.args.get('source')
            if not source_type or source_type not in ('component', 'ticket', 'all', 'query'):
                raise TracError, "Source type not specified or invalid"
            source = req.args.get(source_type)
            dest = req.args.get('destination')
            action = None
            if 'copy' in req.args.keys():
                action = 'copy'
            elif 'move' in req.args.keys():
                action = 'move'
            else:
                raise TracError, 'Action not specified or invalid'
                
            action_verb = {'copy':'Copied', 'move':'Moved'}[action]
            
            # Double check the ticket number is actually a number
            if source_type == 'id':
                try:
                    int(source)
                except ValueError:
                    raise TracError('Value %r is not numeric'%source)
            
            self.log.debug('DatamoverTicketModule: Source is %s (%s)', source, source_type)
            
            query_string = {
                'ticket': 'id=%s'%source,
                'component': 'component=%s'%source,
                'all': 'id!=0',
                'query': source,
            }[source_type]
                
            try:
                # Find the ids we want
                ids = None
                if source_type == 'ticket': # Special case this pending #T4119
                    ids = [int(source)]
                else:
                    self.log.debug('DatamoverTicketModule: Running query %r', query_string)
                    ids = [x['id'] for x in Query.from_string(self.env, query_string).execute(req)]
                    self.log.debug('DatamoverTicketModule: Results: %r', ids)
                    
                dest_db = _open_environment(dest).get_db_cnx()
                for id in ids:
                    copy_ticket(self.env, dest, id, dest_db)
                dest_db.commit()
                    
                if action == 'move':
                    for id in ids:
                        Ticket(self.env, id).delete()
                    
                if ids:
                    req.hdf['datamover.message'] = '%s tickets %s'%(action_verb, ', '.join([str(n) for n in ids]))
                else:
                    req.hdf['datamover.message'] = 'No tickets %s'%(action_verb.lower())
            except TracError, e:
                req.hdf['datamover.message'] = "An error has occured: \n"+str(e)
                self.log.warn(req.hdf['datamover.message'], exc_info=True)
            


        req.hdf['datamover.components'] = components
        req.hdf['datamover.envs'] = envs
        return 'datamover_ticket.cs', None


