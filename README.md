botgarden_project
=================

This Django project supports several webapps used by the UC Botanical Garden.

It is based on the "cspace_django_project" which provide basic authentication of webapps against
the configured CSpace server (see the documentation for this project on GitHub).

Some things to note when deploying this project:

* Most webapps require a config file, and an example configuration file, is included in the app's directory.
Each of these needs to be copied to the *project configuration directory* (config/)
with the file name expected by the webapp (usually "webapp.cfg" where "webapp" is the
directory name of the webapp) and then edited to specific deployment-specific parameters.

* There are installation and update scripts which deploy these "cspace_django_project"-type projects in UCB's RHEL
environments. These may be found in Tools/deployandrelease repo, which should normally be deployed alongside the
projects themselves.THEN EDITED* to provide specific deployment-specific parameters.