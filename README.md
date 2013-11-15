# ckanext-redmine

This is an extension that provides a contact form for users to contact you about different categories of problems, backed by a [redmine](http://www.redmine.org/) installation.

## Features

This extension provides:

### Contact form 

This (defaults to /contact) that allows a user to contact the data portal owners and send feedback/questions within certain categories. The categories drop-down is populated with the categories from Redmine and so these should be created within Redmine itself (optionally with a default assignee).

In this version of the extension all submitted issues are private (at least if Redmine is configured to be private) and they are not shown on the data portal.

Failure to add the issue to redmine will trigger an email to a system administrator to containing the contact information (so that details are not lost).

### Simple contact-report 

This shows the number of open/closed tickets with links to the youngest and oldest tickets in each state.  The table below shows the number of open/closed tickets for each category and provides a link directly to the Redmine view filtered by that category.  This view is only accessible to system administrators.


## Configuration

1. Create a project, some categories and add a user to redmine.  Go to /settings and click on Authentication and make sure Enable REST web service is checked.

2. Add ```redmine``` to your ckan.plugins.

3. Add the following entries to your ckan .ini file.

```
ckanext.redmine.url = http://<URL_OF_REDMINE_SERVER>
ckanext.redmine.apikey = <API_KEY>
ckanext.redmine.project = <PROJECT_NAME>
```

 * URL_OF_REDMINE_SERVER - The web address of your redmine installation
 
 * API_KEY - The API key of a user with permission to create issues, this can be found at /my/account on your installation, you should click 'Show' underneath the API access key section on the right.
 
 * PROJECT_NAME - This is the short name of the project, for instance a project called "Issues Test" will end up with a short-name like issues-test.  You can see this in the browser address bar when you visit it in redmine.
 
## Future

#### Spam checking

The extension should use mollom (or suchlike) to check for spam submissions.

#### Custom fields

Extension should take advantage of the custom fields to record the relevant dataset/publisher so that issues can be grouped/queried on that data. Currently this is inline in the issue content.

#### Fuller reports

More reports on the processing of issues. Charts of velocity based on issue state, changes of state and grouped by publisher/dataset.

#### User tracking of issues

Users should be able to view, on the site, issues that they have created and be able to respond to them (with their feedback being added to Redmine).

#### Publisher access to issues

Publishers should be able to obtain a view that shows the issues that are relevant to them, or are about their datasets. Eventually they should be able to response/close issues as well.

#### Email integration

Responses to issues are likely to take place in users' inboxes, and it would be more efficient, and valuable, if ckanext-redmine were able to be responsible for sending the messages, and also for integrating the responses.  This may require new forms for responding to issues and delivering/retrieving email on each item.




