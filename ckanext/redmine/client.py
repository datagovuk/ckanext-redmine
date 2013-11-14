from pylons import config
from urlparse import urljoin

import logging
import json
import requests

log = logging.getLogger(__name__)

_categories = {}

def _make_call(path, method="GET", data=None):
    server = config.get('ckanext.redmine.url')
    apikey = config.get('ckanext.redmine.apikey')
    project = config.get('ckanext.redmine.project')

    url = urljoin(server, path)
    headers = {"X-Redmine-API-Key": apikey}
    if method == "GET":
        response = requests.get(url,headers=headers)
    else:
        print "data is ", data
        headers['Content-type'] = 'application/json'
        response = requests.post(url,headers=headers, data=data)
    if response.status_code not in [200, 201, 304]:
        log.error("Redmine request failed with code %d: %s" % (response.status_code, path))
        return None

    return json.loads(response.content)


def load_categories():
    global _categories
    if not _categories:
        log.info("Loading redmine categories")
        path = "/projects/{0}/issue_categories.json".format(config.get('ckanext.redmine.project'))
        data = _make_call(path)
        for item in data['issue_categories']:
            _categories[item['name']] = item['id']
    return _categories

def post_issue(issue_dict):
    path = "/issues.json"

    data = {
        "issue":{
                "project_id": config.get('ckanext.redmine.project'),
                "subject": issue_dict["subject"],
                "category_id": issue_dict["category"],
                "description": issue_dict["message"],
                }
    }

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