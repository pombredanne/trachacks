import re

from genshi.builder import Markup, tag
from genshi.filters.transform import Transformer

from pkg_resources import resource_filename

from trac.core import Component, implements
from trac.mimeview.api import Context
from trac.resource import ResourceNotFound
from trac.ticket import TicketSystem
from trac.web.api import ITemplateStreamFilter, IRequestFilter
from trac.web.chrome import ITemplateProvider, add_script
from trac.web.href import Href

from tracremoteticket.api import RemoteTicketSystem
from tracremoteticket.links import RemoteLinksProvider
from tracremoteticket.model import RemoteTicket
from trac.wiki.formatter import format_to_oneliner

__all__ = ['RemoteTicketModule']

class RemoteTicketModule(Component):
    implements(ITemplateProvider,
               IRequestFilter,
               ITemplateStreamFilter,
               )

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return [('tracremoteticket', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return []
    
    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        # If linked_val request argument matches the URL of a known
        # remote site then:
        #  - Parse it, storing the result in linked_remote_val
        #  - Remove the linked_val argument, so trac doesn't also process it
        if 'linked_val' in req.args:
            linked_val = req.args['linked_val']
            patt = re.compile(r'(.+)/ticket/(\d+)')
            for name, site in RemoteTicketSystem(self.env)._intertracs.items():
                m = patt.match(linked_val)
                if m:
                    remote_base, remote_tkt_id = m.groups()
                    if remote_base == site['url'].rstrip('/'):
                        req.args['linked_remote_val'] = '%s:#%s' \
                                                        % (name, remote_tkt_id)
                        del req.args['linked_val']
                        break
        return handler
    
    def post_process_request(self, req, template, data, content_type):
        if req.path_info.startswith('/ticket') and data:
            return self._do_ticket(req, template, data, content_type)
        elif req.path_info.startswith('/newticket') and data:
            return self._do_newticket(req, template, data, content_type)
        else:
            return (template, data, content_type)
        
    def _do_ticket(self, req, template, data, content_type):
        if 'ticket' in data and 'linked_tickets' in data:
            ticket = data['ticket']
            context = Context.from_request(req, ticket.resource)
            
            # Add name:#n links to link fields of Ticket instance when
            # flowing from storage to browser
            if req.method == 'GET':
                RemoteLinksProvider(self.env).augment_ticket(ticket)
            
            # Rerender link fields
            for field in data['fields']:
                if field['type'] == 'link':
                    name = field['name']
                    field['rendered'] = format_to_oneliner(self.env, context,
                                                           ticket[name])
            
            # Add RemoteTicket objects for linked issues table, and pass list
            # of rejects that could not be retrieved
            linked_tickets, linked_rejects = self._remote_tickets(ticket,
                                                                  context)
            data['linked_tickets'].extend(linked_tickets)
            data['linked_rejects'].extend(linked_rejects)
        
        # Provide list of remote sites if newlinked form options are present
        if 'newlinked_options' in data:
            remote_sites = RemoteTicketSystem(self.env).get_remote_tracs()
            data['remote_sites'] = remote_sites
        
        return (template, data, content_type)
        
    def _do_newticket(self, req, template, data, content_type):
        link_remote_val = req.args.get('linked_remote_val', '')
        pattern = RemoteTicketSystem(self.env).REMOTES_RE
        lrv_match = pattern.match(link_remote_val)
        link_end = req.args.get('linked_end', '')
        ends_map = TicketSystem(self.env).link_ends_map
        
        if ('ticket' in data and lrv_match and link_end in ends_map):
            ticket = data['ticket']
            remote_name = lrv_match.group(1)
            remote_id = lrv_match.group(2)
            remote_ticket = RemoteTicket(self.env, remote_name, remote_id,
                                         refresh=True)
            link_fields = [f for f in ticket.fields if f['name'] == link_end]
            copy_field_names = link_fields[0]['copy_fields']
            
            ticket[link_end] = link_remote_val
            for fname in copy_field_names:
                ticket[fname] = remote_ticket[fname]
            
            data['remote_ticket'] = remote_ticket
            
        return (template, data, content_type)
    
    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, data):
        if 'ticket' in data and 'remote_sites' in data:
            add_script(req, 'tracremoteticket/js/remoteticket.js')
            
            transf = Transformer('//select[@id="linked-end"]')
            label = tag.label(' in ', for_='remote-site')
            local = tag.option('this project', value=req.href.newticket(),
                               selected='selected')
            remotes = [tag.option(rs['title'], 
                                  value=Href(rs['url']).newticket())
                       for rs in data['remote_sites']]
            select = tag.select([local] + remotes, id='remote-site')
            content = label + select
            stream |= transf.after(content)
            
        return stream
    
    def _remote_tickets(self, ticket, context):
        link_fields = [f for f in ticket.fields if f['type'] == 'link']
        rts = RemoteTicketSystem(self.env)
        
        linked_tickets = []
        linked_rejects = []
        for field in link_fields:
            for link_name, link in rts.parse_links(ticket[field['name']]):
                tkt_fmt = format_to_oneliner(self.env, context,
                                             '%s:#%s' % (link_name, link))
                try:
                    tkt = RemoteTicket(self.env, link_name, link)
                    linked_tickets.append((field['label'], tkt_fmt, tkt))
                except ResourceNotFound:
                    linked_rejects.append((field['label'], tkt_fmt))
        
        return linked_tickets, linked_rejects

