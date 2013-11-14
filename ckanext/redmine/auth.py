from pylons.i18n import _

def issue_create(context, data_dict=None):
    return {'success': True}

def issue_list(context, data_dict=None):
    import ckan.new_authz as new_authz
    model = context['model']
    user = context.get('user')
    user_obj = model.User.get(user)

    if user_obj and new_authz.is_sysadmin(user_obj):
        return {'success': True}

    return {'success': False,
            'msg': _('User %s not authorized to list issues') % user}
