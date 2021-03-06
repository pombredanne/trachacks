from traclegos.project import TracProject
from paste.script import templates

var = templates.var

class SimpleTracProject(TracProject):
    _template_dir = 'template'
    summary = 'Simple trac project template'

    vars = [ var('basedir', 'base directory for trac',
                 default='.'),
             var('domain', 'domain name where this project is to be served', 
                 default='localhost'),
             ]

