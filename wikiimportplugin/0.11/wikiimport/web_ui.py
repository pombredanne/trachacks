from trac.core import *
from trac.web.chrome import ITemplateProvider, add_stylesheet
from trac.admin.web_ui import IAdminPanelProvider
from trac.config import ConfigurationError
from trac.env import Environment
from operator import itemgetter
from trac.wiki.api import WikiSystem
from trac.wiki.model import WikiPage
from trac.util import get_reporter_id

class WikiImportAdmin(Component):

	implements(IAdminPanelProvider, ITemplateProvider)

	# ITemplateProvider methods
	def get_templates_dirs(self):
		from pkg_resources import resource_filename
		return [resource_filename(__name__, 'templates')]
        
	def get_htdocs_dirs(self):
		from pkg_resources import resource_filename
		return [('wikiimport', resource_filename(__name__, 'htdocs'))]

	# IAdminPanelsProvider methods
	def get_admin_panels(self, req):
		if req.perm.has_permission('WIKI_ADMIN'):
			yield ('wiki', 'Wiki', 'wikiimport', 'Import')

	# IAdminPanelProvider methods
	def render_admin_panel(self, req, cat, page, component):
		""" Just a lightweight front controller. Specific logic is implemented in _controller_* methods. """

		# Default controller	
		controller = self._controller_init

		if req.method == 'POST':
			if req.args.get('wikiimport_action_preview'):
				controller = self._controller_preview
			elif req.args.get('wikiimport_action_import'):
				controller = self._controller_import

		return controller(req, cat, page, component)

	# Controllers
	def _controller_init(self, req, cat, page, component):
		""" Default controller. Displays instance selection page. """

		# Data to be passed to the view
		data = {'instances': []}

		# Collect preconfigured instances specifications
		data['instances'] = self._get_instances_specs(self.env.config.options('wiki-import'))

		# Alphabetical sort
		sorted_data_instances = sorted(data['instances'], key=itemgetter('name'))
		data['instances'] = sorted_data_instances

		# Raise a configuration exception if no instances are configured
		if len(data['instances']) < 1:
			raise ConfigurationError("Please first declare trac instances in your project's trac.ini")

		return 'admin_wikiimport_init.html', data

	def _controller_preview(self, req, cat, page, component):
		""" Compares source and destination wiki pages to let the user know which contents may be overriden during the import. """

		# Data to be passed to view
		data = {}
		data['instance_id'] = req.args.get('wikiimport_instance_id')

		# Get operations to be performed
		data['operations'] = self._get_page_operations(req.args.get('wikiimport_instance_id'))

		# Add stylesheet to view
		add_stylesheet(req, 'wikiimport/css/wikiimport.css');

		# Render view
		return 'admin_wikiimport_preview.html', data

	def _controller_import(self, req, cat, page, component):
		""" Performs import. """

		# Data to be passed to view
		data = {}

		# For simplicity's sake
		source_instance_id = req.args.get('wikiimport_instance_id')

		# Get operations to be performed
		data['operations'] = self._get_page_operations(source_instance_id)

		# Update local wiki
		source_env = self._get_instance_env(source_instance_id)
		for page, operation in data['operations'].items():
			source_page = WikiPage(source_env, page)
			local_page = WikiPage(self.env, page)
			local_page.text = source_page.text
			local_page.save(
				get_reporter_id(req, 'author'), 
				'Importing pages from "%s" using [http://trac-hacks.org/wiki/WikiImport WikiImport plugin].' % source_instance_id, 
				req.remote_addr
			)

		# Add stylesheet to view
		add_stylesheet(req, 'wikiimport/css/wikiimport.css');

		return 'admin_wikiimport_import.html', data

	# Helpers
	def _get_page_operations(self, source_instance_id):

		operations = {}

		# Open source and destination wikis
		source_env = self._get_instance_env(source_instance_id)
		source_wiki_system = WikiSystem(source_env)
		dest_wiki_system = WikiSystem(self.env)

		# Extract wiki pages from both wikis 
		local_pages = []
		for page in dest_wiki_system.get_pages():
			local_pages.append(page)
		source_pages = []
		for page in source_wiki_system.get_pages():
			source_pages.append(page)
			operations[page] = 'create'

		# Create operations list
		for page in local_pages:
			if page in source_pages:
				operations[page] = 'update'

		# Do not update pages with identical contents
		for page, operation in operations.items():
			local_page = WikiPage(self.env, page)
			source_page = WikiPage(source_env, page)
			if local_page.text == source_page.text:
				del operations[page]	

		return operations

	def _get_instance_env(self, requested_instance_id):

		for option, value in self.env.config.options('wiki-import'):
			parts = option.split('.')
			instance_id = parts[0]
			instance_prop = parts[1]
			if instance_id == requested_instance_id:
				if instance_prop == 'path':
					instance_path = value 
					try: 
						env = Environment(instance_path)
					except IOError:	
						raise TracError('Could not instanciate environment "%s". Please check your trac.ini file.' % requested_instance_id);

		return env 

	def _get_instances_specs(self, options):

		specs = []
		for option, value in options:
			parts = option.split('.')
			instance_id = parts[0]
			instance_prop = parts[1]
			if instance_prop == 'name':
				instance_name = value 
				specs.append({'name': instance_name, 'id': instance_id})

		return specs
