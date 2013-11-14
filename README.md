# ckanext-redmine

This is an extension that provides a contact form for users to contact you about different categories of problems, backed by a [redmine](http://www.redmine.org/) installation.



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