import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Data(db.Model):
    _id = db.StringProperty()
    content = db.TextProperty()

class Index(webapp.RequestHandler):
    def filter_id(self, _id):
        # filter out the path used for the _id
        return filter(lambda c: c.isalnum(), _id)
    
    def get(self, _id):
        if _id == 'favicon.ico':
            self.error(404)
        else:
            template_values = { }
            
            _id = self.filter_id(_id)
            
            if _id:
                template_values['initial_text'] = self.read_file(_id)
            else:
                template_values['initial_text'] = 'To start using autopybook write some id and press the "Load" button (or hit enter).'
            
            template_values['initial_id'] = _id
            template_values['initial_expl'] = 'Write some text below and it will be auto-saved for your id.' if _id else ''
            
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))
    
    def post(self, _id):
        _id = self.filter_id(_id)
        self.write_file(_id, self.request.body.decode('utf-8'))
    
    def read_file(self, _id):
        content = ''
        datas = db.GqlQuery("SELECT * FROM Data WHERE _id = :1", _id)
        for data in datas:
            content = data.content
        return content
    
    def write_file(self, _id, content):
        datas = db.GqlQuery("SELECT * FROM Data WHERE _id = :1", _id)
        found = False
        for data in datas:
            data.content = content
            data.put()
            found = True
        if not found:
            data = Data()
            data._id = _id
            data.content = content
            data.put()

application = webapp.WSGIApplication([(r'/(.*)', Index)])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
