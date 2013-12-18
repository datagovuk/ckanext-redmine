from pylons import config
import datetime
import dateutil
import logging
from dateutil.parser import parse
import ckan.lib.helpers as helpers
from ckan.lib.base import h, BaseController, abort, g
from ckan.lib.navl.dictization_functions import DataError, unflatten, validate
from ckan.logic import tuplize_dict, clean_dict, parse_params, flatten_to_string_key
from ckanext.dgu.plugins_toolkit import (render, c, request, _,
    ObjectNotFound, NotAuthorized, ValidationError, get_action, check_access)

log = logging.getLogger(__name__)

class RedmineController(BaseController):

    def report(self):
        """
        Generates a simple report of open/closed counts both as totals
        and per-category
        """
        from ckanext.redmine.client import RedmineClient
        import ckan.model as model

        # Ensure only sysadmins can view this report for now.
        try:
            context = {'model':model,'user': c.user}
            check_access('issue_list',context)
        except NotAuthorized, e:
            h.redirect_to('/')

        # Obtain the category list and the URLs we need for links to
        # redmine.
        client = RedmineClient("general")
        c.categories = client.load_categories()
        c.issues_url = client.get_issues_url()
        c.issue_url = client.get_single_issue_url()

        # Get the lists of open and closed issues.
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

        # Process the open issues to find the category totals and the dates
        # of the oldest and newest issues
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

        # Process the closed issues to find the category totals and the dates
        # of the oldest and newest issues
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

    def _save_on_fail(self, data):
        """
        Handle a failure to create an issue by emailing the details to
        the configured email address
        """
        from ckan.lib.mailer import mail_recipient
        addresses = config.get('ckanext.redmine.error_email', '').split(',')
        if not addresses:
            log.error("No backup email address to save data: {0}".format(data))
            return

        email_msg = """
            REDMINE server not available

            Sender: {0}
            Email: {1}
            Subject: {2}
            Message: {3}
        """.format(data.get('name'), data.get('email'),data.get('subject'), data.get('message'))

        for recipient in addresses:
            mail_recipient(recipient,
                           recipient,
                           "ckanext-redmine failure",
                           email_msg)



    def contact(self, name=None):
        """
        This action allows users to create an issue by filling in a contact
        form.
        """
        import ckan.model as model
        from ckanext.redmine.client import RedmineClient

        print name
        extra_vars = {
            "data": {},
            "errors": {}
        }

        client = RedmineClient(name)
        c.categories = client.load_categories()
        c.name = name

        if request.method == 'POST':
            data = clean_dict(unflatten(tuplize_dict(parse_params(request.POST))))
            context = {'model': model, 'session': model.Session,
                       'user': c.user}

            # Create the issue with the data we were passed.
            try:
                newid = get_action('issue_create')(context, data)
                if newid is None:
                    self._save_on_fail(data)
                    h.flash_success(_('Thank you for contacting us'.format(newid)))
                else:
                    h.flash_success(_('Thank you for contacting us, please quote #{0} in future correspondence'.format(newid)))

                h.redirect_to(str(data.get('referer', '/')))
            except ValidationError, e:
                extra_vars["errors"] = e.error_dict
                extra_vars["error_summary"] = e.error_summary
                extra_vars["data"] = data
                c.category_id = data.get('category','')

        if request.method == 'GET':
            if not c.categories:
                pass  # We have a problem, we couldn't get categories. We should bail.

            # Pre-fill some data we may already have.
            extra_vars['data']['name'] = c.userobj.fullname if c.userobj else ''
            extra_vars['data']['email'] = c.userobj.email if c.userobj else ''
            # We will use this to send the user to the appropriate place when finished.
            extra_vars['data']['referer'] = request.referer or '/'

            # If dataset appears on the URL, record it. We *could* pull this from the
            # referer but safer to be explicit.
            dataset_name = request.GET.get('dataset')
            if dataset_name:
                extra_vars['data']['dataset'] = h.url_for(controller='package', action='read', id=dataset_name, qualified=True)

            #if category:
            #    # Match any category in the URL with the value we retrieved (which may
            #    # be mixed-case) from redmine
            #    for k, v in c.categories.iteritems():
            #        if k.lower() == category:
            #            c.category_id = v

        return render('ckanext/redmine/contact.html', extra_vars=extra_vars)

    def _humanize(self, dt, default="Just now"):
        """
        Returns string representing "time since" e.g.
        3 days ago, 5 hours ago etc.
        Original by Dan Jacob - http://flask.pocoo.org/snippets/33/ but changed
        to make timezone aware comparisons possible.
        """
        import time

        # Make sure this date is timezone aware
        now = datetime.datetime.now(dateutil.tz.tzutc())

        diff = now - dt
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
