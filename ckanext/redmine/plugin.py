import json
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
    p.implements(p.ITemplateHelpers, inherit=True)

    def configure(self, config):
        pass

    def update_config(self, config):
        from ckanext.redmine.client import RedmineClient
        p.toolkit.add_template_directory(config, 'templates')

        RedmineClient._default_name = config.get("ckanext.redmine.default_name","")

        # Check we have the required config
        config_file = config.get('ckanext.redmine.config')
        if not config_file:
            log.error("Unable to load redmine config file")

        with open(config_file, 'r') as f:
            RedmineClient._config = json.loads(f.read())


    def get_helpers(self):
        """
        A dictionary of extra helpers that will be available to provide
        redmine specific helpers to the templates.
        """
        helper_dict = {
            'redmine_is_installed': lambda: True
        }
        return helper_dict



    def before_map(self, map):
        controller = 'ckanext.redmine.controller:RedmineController'
        map.connect('/contact/:name',
                    controller=controller, action='contact')
        map.connect('/contact',
                    controller=controller, action='contact')
        map.connect('/contact-report',
                    controller=controller, action='report')
        return map

    def get_auth_functions(self):
        from ckanext.redmine.auth import issue_list
        return {
            "issue_list": issue_list
        }

    def get_actions(self):
        from ckanext.redmine.logic import issue_create
        return {
            'issue_create': issue_create
        }
