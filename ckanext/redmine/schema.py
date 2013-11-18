from ckan.lib.navl.validators import not_empty,ignore_missing

def get_issue_schema():
    return {
        'message': [not_empty, unicode],
        'subject': [not_empty, unicode],
        'name'   : [not_empty, unicode],
        'email'  : [not_empty, unicode],
        'category': [ignore_missing, unicode],

        'dataset': [ignore_missing, unicode]
    }
