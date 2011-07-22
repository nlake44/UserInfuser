""" Fantasm: A taskqueue-based Finite State Machine for App Engine Python

Docs and examples: http://code.google.com/p/fantasm/

Copyright 2010 VendAsta Technologies Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.



Main module for fantasm implementation.

This module should be specified as a handler for fantasm URLs in app.yaml:

  handlers:
  - url: /fantasm/.*
    login: admin
    script: fantasm/main.py
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from fantasm import handlers, console

def createApplication():
    """Create new WSGIApplication and register all handlers.

    Returns:
        an instance of webapp.WSGIApplication with all fantasm handlers registered.
    """
    return webapp.WSGIApplication([
        (r"^/[^\/]+/fsm/.+",       handlers.FSMHandler),
        (r"^/[^\/]+/cleanup/",     handlers.FSMFanInCleanupHandler),
        (r"^/[^\/]+/graphviz/.+",  handlers.FSMGraphvizHandler),
        (r"^/[^\/]+/log/",         handlers.FSMLogHandler),
        (r"^/[^\/]+/?",            console.Dashboard),
    ],
    debug=True)

APP = createApplication()

def main():
    """ Main entry point. """
    import os
    if os.environ.get('SERVER_SOFTWARE') == 'Development/1.0':
        # this seems to be a dev_appserver.py bug. causes unicode errors when trying to process the request
        os.environ['QUERY_STRING'] = str(os.environ['QUERY_STRING'])
    util.run_wsgi_app(APP)

if __name__ == "__main__":
    main()
