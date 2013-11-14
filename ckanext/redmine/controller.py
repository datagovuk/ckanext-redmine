from pylons import config

import ckan.lib.helpers as helpers
from ckan.lib.base import h, BaseController, abort, g
from ckan.lib.navl.dictization_functions import DataError, unflatten, validate
from ckan.logic import tuplize_dict, clean_dict, parse_params, flatten_to_string_key
from ckanext.dgu.plugins_toolkit import (render, c, request, _,
    ObjectNotFound, NotAuthorized, ValidationError, get_action, check_access)


class RedmineController(BaseController):

    def contact(self, category=None):
        import ckan.model as model
        from ckanext.redmine import client

        extra_vars = {
            "data": {},
            "errors": {}
        }

        c.categories = client.load_categories()
        if request.method == 'POST':
            data = clean_dict(unflatten(tuplize_dict(parse_params(request.POST))))

            context = {'model': model, 'session': model.Session,
                       'user': c.user}

            try:
                newid = get_action('issue_create')(context, data)

                h.flash_success(_('Thank you for contacting us, please quote #{0} in future correspondence'.format(newid)))
                #h.redirect_to(extra_vars['data'].get('referer', '/'))
            except ValidationError, e:
                extra_vars["errors"] = e.error_dict
                extra_vars["error_summary"] = e.error_summary
                extra_vars["data"] = data
                c.category_id = data['category']

        if request.method == 'GET':
            extra_vars['data']['name'] = c.userobj.fullname if c.userobj else ''
            extra_vars['data']['email'] = c.userobj.email if c.userobj else ''
            extra_vars['data']['referer'] = request.referer or '/'

            dataset_name = request.GET.get('dataset')
            if dataset_name:
                extra_vars['data']['dataset'] = h.url_for(controller='package', action='read', id=dataset_name, qualified=True)

            if category:
                for k, v in c.categories.iteritems():
                    if k.lower() == category:
                        c.category_id = v

        return render('ckanext/redmine/contact.html', extra_vars=extra_vars)

    def _save(self, data):
        pass