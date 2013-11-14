
from ckanext.dgu.plugins_toolkit import (render, c, request, _,
    ObjectNotFound, NotAuthorized, ValidationError, get_action, check_access)
from ckan.lib.navl.dictization_functions import validate
from ckan.lib.base import h

from ckanext.redmine.client import post_issue
from ckanext.redmine.schema import get_issue_schema
import logging

log = logging.getLogger(__name__)

def issue_create(context, data_dict):
    schema = get_issue_schema()
    data, errors = validate(data_dict, schema, context)
    log.debug('issue_create validate_errs=%r user=%s data=%r',
              errors, context.get('user'), data_dict)

    if errors:
        raise ValidationError(errors)

    msg = """Full name: {0}
Email: {1}
Dataset: {2}
----

{3}
    """.format( data_dict['name'], data_dict['email'],
                data_dict.get('dataset', 'N/A'),
                data_dict['message'])
    data_dict['message'] = msg
    return post_issue(data_dict)
