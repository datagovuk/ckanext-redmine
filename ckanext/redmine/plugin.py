import logging
import ckan.plugins as p
import ckan.lib.helpers as h
import ckan.plugins.toolkit as t

log = logging.getLogger(__name__)

class RedminePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IAuthFunctions, inherit=True)
    p.implements(p.IActions, inherit=True)

    def configure(self, config):
        pass

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')

        # Check we have the required config
        server = config.get('ckanext.redmine.url')
        apikey = config.get('ckanext.redmine.apikey')
        project = config.get('ckanext.redmine.project')

        if not server:
            log.error("Redmine server location not specified in config")
        if not apikey:
            log.error("Redmine APIKey not specified in config")
        if not project:
            log.error("Redmine project short-name not specified in config")


    def before_map(self, map):
        controller = 'ckanext.redmine.controller:RedmineController'
        map.connect('/contact/{category:.*}',
                    controller=controller, action='contact')
        map.connect('/contact',
                    controller=controller, action='contact')
        return map

    def get_auth_functions(self):
        return {}

    def get_actions(self):
        from ckanext.redmine.logic import issue_create
        return {
            'issue_create': issue_create
        }
