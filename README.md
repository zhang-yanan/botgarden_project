botgarden_project
=================

This Django project supports several webapps used by the UC Botanical Garden.

Is is based on the "cspace_django_project" which provide basic authentication of webapps against
the configured CSpace server (see the documentation for this project on GitHub).

Some things to note when deploying this project:

* Each webapp has an example configuration file, usually something like "exampleWebappname.cfg" in
the application's root directory. Each of these needs to be copied to the project config directory
with the file name expected by the webapp (usually "webapp.cfg" where "webapp" is the
directory name of the webapp) *AND THEN EDITED* to provide specific deployment-specific parameters.