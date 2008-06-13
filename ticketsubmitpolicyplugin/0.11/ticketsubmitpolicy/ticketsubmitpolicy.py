# Plugin for trac 0.11

import re

from genshi.builder import tag
from genshi.core import Markup
from genshi.filters import Transformer

from interface import ITicketSubmitPolicy

from trac.core import *
from trac.admin.api import IAdminPanelProvider
from trac.web import ITemplateStreamFilter
from trac.web.chrome import ITemplateProvider


def camelCase(string):
    """returns the camelCase representation of a string"""

    args = string.split()
    args = [args[0]] + [ i.capitalize() for i in args[1:] ]
    return ''.join(args)


class TicketSubmitPolicyPlugin(Component):
    """
    enforce a policy for allowing ticket submission based on fields
    """

    implements(ITemplateStreamFilter) 
    policies = ExtensionPoint(ITicketSubmitPolicy)

    comparitors = { 'is': 1,
                    'is not': 1,
                    'is in': 'Array',
                    'is not in': 'Array' }

    def policy_dict(self):
        retval = {}
        for policy in self.policies:
            retval[policy.name()] = policy
        return retval

    def parse(self):
        """
        parse the [ticket-submit-policy] section of the config for policy rules
        """

        section = dict([i for i in self.config.options('ticket-submit-policy')])

        def parse_list(string):
            return [ i.strip() for i in string.split(',') if i.strip()] 

        policies = {} 
        for key in section:
            try:
                name, action = key.split('.', 1)
            except ValueError:
                self.log.error('invalid key: %s' % key) # XXX log this better
                continue
            if not policies.has_key(name):
                policies[name] = {}

            if action == 'condition':
                condition = section[key]

                conditions = condition.split('&&')

                for condition in conditions:

                    # look for longest match to prevent substring matching
                    comparitors = sorted(self.comparitors.keys(), key=lambda x: len(x), reverse=True)
                    match = re.match('.* (%s) .*' % '|'.join(comparitors), condition)

                    if match:
                        comparitor = str(match.groups()[0]) # needs to be a str to be JS compatible via repr
                        field, value = [i.strip() for i in condition.split(comparitor, 1)]
                        field = str(field)
                        if self.comparitors[comparitor] == 'Array':
                            value = parse_list(value)

                        else:
                            value = str(value)

                        if 'condition' not in policies[name]:
                            policies[name]['condition'] = []
                        policies[name]['condition'].append(dict(field=field,value=value,comparitor=comparitor))
                            
                    else:
                        self.log.error("Invalid condition: %s" % condition)
                                        
                continue

            if not policies[name].has_key('actions'):
                policies[name]['actions'] = []
            args = parse_list(section[key])
            policies[name]['actions'].append({'name': action, 'args': args})

        for policy in policies:
            # empty condition ==> true
            if not policies[policy].has_key('condition'):
                policies[policy]['condition'] = []

        return policies

    # method for ITemplateStreamFilter
    def filter_stream(self, req, method, filename, stream, data):

        if filename == 'ticket.html':

            # setup variables
            javascript = [self.javascript()]

            onload = []
            onsubmit = []
            policy_dict = self.policy_dict()

            # add JS functions to the head block
            for policy in self.policies:

                policy_javascript = policy.javascript()
                if policy_javascript:
                    javascript.append(policy_javascript)

            policies = self.parse()
            
            for name, policy in policies.items():

                # insert the condition into the JS
                conditions = policy['condition']
                conditions = ["{field: '%s', comparitor: %s, value: '%s'}" % (condition['field'], 
                                                                              camelCase(condition['comparitor']),
                                                                              condition['value'])
                              for condition in conditions]
                condition = '%s = [ %s ];' % (name, ', '.join(conditions))
                javascript.append(condition)

                # find the correct handler for the policy
                for action in policy['actions']:
                    handler =  policy_dict.get(action['name'])
                    if handler is None:
                        self.log.error('No ITicketSubmitPolicy found for "%s"' % action['name'])
                        continue
                
                    # filter the stream
                    stream = handler.filter_stream(stream, name, policy['condition'], *action['args'])


                    # add other necessary JS to the page
                    policy_onload = handler.onload(name, policy['condition'], *action['args'])
                    if policy_onload:
                        onload.append(policy_onload)
                    policy_onsubmit = handler.onsubmit(name, policy['condition'], *action['args'])
                    if policy_onsubmit:
                        onsubmit.append(policy_onsubmit)

            # insert onload, onsubmit hooks if supplied
            if onload:
                javascript.append(self.onload(onload))
                stream |= Transformer("body").attr('onload', 'load()')
            if onsubmit:
                javascript.append(self.onsubmit(onsubmit))
                stream |= Transformer("//form[@id='propertyform']").attr('onsubmit', 'return onsubmit')

            # insert head javascript
            if javascript:
                javascript = '\n%s\n' % '\n'.join(javascript)
                javascript = tag.script(Markup(javascript), **{ "type": "text/javascript"})
                
                stream |= Transformer("head").append(javascript)

        return stream

    ### methods returning JS

    def onload(self, items):
        return """
function load()
{
%s
}
""" % '\n'.join(items)


    def onsubmit(self, items):
        """returns text for the onsubmit JS function to be inserted in the head"""
        message = """message = %s
if (message != true)
{
errors[errors.length] = message;
}
"""
        messages = '\n'.join([(message % item) for item in items])

        return """
function onsubmit()
{

var errors = new Array();
%s
if (errors.length)
{

if (errors.length == 1)
{
error_msg = errors[0];
}
else
{
error_msg = errors.join("\\n");
}
alert(error_msg);
return false;

}

return true;
}
""" % messages


    def javascript(self):
        """head javascript required to enforce ticket submission policy"""
        # XXX this should probably go into a separate file

        string = """
function getValue(id)
{
var x=document.getElementById(id);
return x.options[x.selectedIndex].text;
}

function is(x, y)
{
return (x == y);
}

function isNot(x, y)
{
return (x != y);
}

function isIn(x, y)
{
for (index in y)
{

if(x == y[index])
{
return true;
}

}
return false;
}

function isNotIn(x, y)
{
return !isIn(x,y);
}

function condition(policy)
{
    length = policy.length;
    for ( var i=0; i != length; i++ )
        {
            field = getValue('field-' + policy[i].field);
            comparitor = policy[i].comparitor;
            value = policy[i].value;

            if ( !comparitor(field, value) )
                {
                    return false;
                }
        }
    return true;
}

function policytostring(policy)
{
    // this should be replaced by a deCamelCase function
    names = { is: 'is', isNot: 'is not', isIn: 'is in', isNotIn: 'is not in' }

    var strings = new Array(policy.length);
    for ( var i=0; i != policy.length; i++ )
    {
        funcname = names[policy[i].comparitor.name];
        strings[i] = policy[i].field + ' ' + funcname + ' ' + policy[i].value;
    }
    return strings.join(' and ');

}

"""
        return string

    ### methods for IAdminPanelProvider

    def get_admin_panels(self, req):
        """Return a list of available admin panels.
        
        The items returned by this function must be tuples of the form
        `(category, category_label, page, page_label)`.
        """
        return []

    def render_admin_panel(self, req, category, page, path_info):
        """Process a request for an admin panel.
        
        This function should return a tuple of the form `(template, data)`,
        where `template` is the name of the template to use and `data` is the
        data to be passed to the template.
        """
        
    ### methods for ITemplateProvider

    def get_htdocs_dirs():
        """Return a list of directories with static resources (such as style
        sheets, images, etc.)

        Each item in the list must be a `(prefix, abspath)` tuple. The
        `prefix` part defines the path in the URL that requests to these
        resources are prefixed with.
        
        The `abspath` is the absolute path to the directory containing the
        resources on the local file system.
        """

    def get_templates_dirs():
        """Return a list of directories containing the provided template
        files.
        """
