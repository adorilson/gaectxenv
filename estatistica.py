
import cgi
import os
import urllib
import wsgiref.handlers
from datetime import datetime

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import rest


class Estatistica(db.Model):
    local = db.StringProperty()
    data = db.DateTimeProperty()
    unidade = db.StringProperty()
    valor = db.StringProperty()
    parametro = db.StringProperty()

def estatistica_key(estatistica_name=None):
  """Constructs a Datastore key for a Estatistica entity with estatistica_name."""
  return db.Key.from_path('Estatistica', estatistica_name or 'default_estatistica')


class MainPage(webapp.RequestHandler):
    def get(self):
        estatistica_query = Estatistica.all().ancestor(
            estatistica_key('estatistica_name')).order('-data')
        estatisticas = estatistica_query.fetch(10)

        template_values = {
            'estatisticas': estatisticas,
        }

        path = os.path.join(os.path.dirname(__file__), 'index_estatistica.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        estatistica = Estatistica(parent=estatistica_key('estatistica_name'))

        estatistica.local = self.request.get('local')
        data = self.request.get('data').split('+')[0]
        estatistica.data = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
        estatistica.parametro = self.request.get('parametro')
        estatistica.unidade = self.request.get('unidade')
        estatistica.valor = self.request.get('valor')
        
        estatistica.put()

class RestDispatcher(rest.Dispatcher):
    def initialize(self, request, response):
        super(RestDispatcher, self).initialize(request, response)
        self.request.headers['Accept'] = 'application/json'
        self.response.headers['Content-Type'] = 'application/json'

application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/rest/.*', RestDispatcher)
], debug=True)


## configure the rest dispatcher to know what prefix to expect on request urls
rest.Dispatcher.base_url = "/rest"
rest.Dispatcher.add_models({
  "estatistica": Estatistica})

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
