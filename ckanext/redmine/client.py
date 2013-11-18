from pylons import config
from urlparse import urljoin

import logging
import json
import requests

log = logging.getLogger(__name__)

_categories = {}


def _make_call(path, method="GET", data=None):
    """ Makes the actual HTTP request to the redmine server """
    server = config.get('ckanext.redmine.url')
    apikey = config.get('ckanext.redmine.apikey')
    project = config.get('ckanext.redmine.project')

    url = urljoin(server, path)
    headers = {"X-Redmine-API-Key": apikey}
    if method == "GET":
        response = requests.get(url,headers=headers)
    else:
        headers['Content-type'] = 'application/json'
        response = requests.post(url,headers=headers, data=data)
    if response.status_code not in [200, 201, 304]:
        log.error("Redmine request failed with code %d: %s" % (response.status_code, path))
        return None

    return json.loads(response.content)


def load_categories():
    """
    Returns a dictionary of category=>id from redmine, or the cache if we have already
    fetched it previously.
    """
    global _categories
    if not _categories:
        log.info("Loading redmine categories")
        path = "/projects/{0}/issue_categories.json".format(config.get('ckanext.redmine.project'))
        data = _make_call(path)
        if not data:
            log.error("Failed to get categories")
            return _categories

        for item in data['issue_categories']:
            _categories[item['name']] = item['id']
    return _categories

def post_issue(issue_dict):
    """
    Creates a new issue
    """
    path = "/issues.json"

    data = {
        "issue":{
                "project_id": config.get('ckanext.redmine.project'),
                "subject": issue_dict["subject"],
                "description": issue_dict["message"],
                }
    }
    if issue_dict.get("category"):
        data["issue"]["category_id"] = issue_dict["category"]

    extra = {}
    for k, v in issue_dict.iteritems():
        if k.startswith('_'):
            extra[k[1:]] = v
    if extra:
        data['custom_field_values'] = extra

    response_data = _make_call(path, method="POST", data=json.dumps(data))
    if not response_data:
        return None
    return response_data['issue']['id']

def get_issues_count(status='open'):
    """ Gets the number of issues with the specified state """
    path = "/projects/{0}/issues.json?limit=100&status_id={1}&sort=created_on:desc".format(
        config.get('ckanext.redmine.project'), status)
    return _make_call(path)

    #To fetch issues created after a certain date (uncrypted filter is ">=2012-03-01") :
#GET /issues.xml?created_on=%3E%3D2012-03-01

def get_issues_url():
    """ Get the URL for filtered issues """
    server = config.get('ckanext.redmine.url')
    project = config.get('ckanext.redmine.project')
    return urljoin(server, "/projects/{0}/issues?sort=status&set_filter=1&f[]=category_id&op[category_id]==&v[category_id][]=".format(project))

def get_single_issue_url():
    """ Get the URL for a single issue """
    server = config.get('ckanext.redmine.url')
    return urljoin(server, "/issues/")


