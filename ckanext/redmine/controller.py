from pylons import config
import datetime
import dateutil
from dateutil.parser import parse
import ckan.lib.helpers as helpers
from ckan.lib.base import h, BaseController, abort, g
from ckan.lib.navl.dictization_functions import DataError, unflatten, validate
from ckan.logic import tuplize_dict, clean_dict, parse_params, flatten_to_string_key
from ckanext.dgu.plugins_toolkit import (render, c, request, _,
    ObjectNotFound, NotAuthorized, ValidationError, get_action, check_access)


class RedmineController(BaseController):

    def _humanize(self, dt, default="Just now"):
        """
        Returns string representing "time since" e.g.
        3 days ago, 5 hours ago etc.
        Thanks to Dan Jacob - http://flask.pocoo.org/snippets/33/
        """
        import time

        now = datetime.datetime.now(dateutil.tz.tzutc())

        diff = now - dt
        print diff
        periods = (
            (diff.days / 365, "year", "years"),
            (diff.days / 30, "month", "months"),
            (diff.days / 7, "week", "weeks"),
            (diff.days, "day", "days"),
            (diff.seconds / 3600, "hour", "hours"),
            (diff.seconds / 60, "minute", "minutes"),
            (diff.seconds, "second", "seconds"),
        )

        for period, singular, plural in periods:
            if period > 0:
                return "%d %s ago" % (period, singular if period == 1 else plural)
            elif period < 0:
                break
        return default

    def report(self):
        from ckanext.redmine import client
        import ckan.model as model

        try:
            context = {'model':model,'user': c.user}
            check_access('issue_list',context)
        except NotAuthorized, e:
            h.redirect_to('/')

        c.categories = client.load_categories()

        c.issues_url = client.get_issues_url()
        c.issue_url = client.get_single_issue_url()

        open_issues = client.get_issues_count(status="open")
        closed_issues = client.get_issues_count(status="closed")

        if not open_issues or not closed_issues:
            c.error = "Cannot connect to Redmine"
            return render('ckanext/redmine/report.html')

        c.open_total = open_issues['total_count']
        c.closed_total = closed_issues['total_count']
        c.open = {}
        c.closed = {}

        c.earliest_open = None
        c.latest_open = None
        c.earliest_open_id = ""
        c.latest_open_id = ""

        utc = dateutil.tz.tzutc()
        for i in open_issues.get('issues'):
            c.open[i['category']['name']] = c.open.get(i['category']['name'], 0)  + 1
            d = parse(i['created_on'], tzinfos=[utc])
            if not c.earliest_open or d < c.earliest_open:
                c.earliest_open = d
                c.earliest_open_id = str(i['id'])
            if not c.latest_open or d > c.latest_open:
                c.latest_open = d
                c.latest_open_id = str(i['id'])

        if c.open_total:
            c.earliest_open = self._humanize(c.earliest_open)
            c.latest_open = self._humanize(c.latest_open)


        c.earliest_closed = None
        c.latest_closed = None
        c.earliest_closed_id = -1
        c.latest_closed_id = -1

        for i in closed_issues.get('issues'):
            c.closed[i['category']['name']] = c.closed.get(i['category']['name'], 0)  + 1
            d = parse(i['updated_on'], tzinfos=[utc])
            if not c.earliest_closed or d < c.earliest_closed:
                c.earliest_closed = d
                c.earliest_closed_id = str(i['id'])
            if not c.latest_closed or d > c.latest_closed:
                c.latest_closed = d
                c.latest_closed_id = str(i['id'])
        if c.closed_total:
            c.earliest_closed = self._humanize(c.earliest_closed)
            c.latest_closed = self._humanize(c.latest_closed)

        return render('ckanext/redmine/report.html')

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
                h.redirect_to(extra_vars['data'].get('referer', '/'))
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