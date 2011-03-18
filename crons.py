#!/usr/bin/env python
# coding: utf-8
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import gdata.spreadsheet.text_db

class Page(db.Model):
  page_id = db.IntegerProperty()
  html = db.TextProperty()

class MakeXML:

    def make(self):
      client = gdata.spreadsheet.text_db.DatabaseClient('kyusuisho.appspot.com@gmail.com', 'ohsiusuyk')
      db = client.GetDatabases(name=u'kyusuisho.appspot.com')[0]
      xml=MakeXML.make_xml(db.GetTables(name=u'root')[0])
      page = Page.gql('WHERE page_id = :1', 10).get()
      if page is None:
        page = Page(page_id=10,html=xml)
      else:
        page.xml = xml
      page.put()

    @classmethod
    def xml_escape(cls,text):
      MakeXML.xml_escape_table = {
        u"&": u"&amp;",
        u'"': u"&quot;",
        u"'": u"&apos;",
        u">": u"&gt;",
        u"<": u"&lt;",
      }
      return u"".join(MakeXML.xml_escape_table.get(c,c) for c in text)

    @classmethod
    def make_xml(cls,table):
      xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<document>"
      scripts = []
      current_prefecture = u"";
      for record in table.GetRecords(1, 999999999):
        if current_prefecture != record.content[u"都道府県"]:
          xml += u"" if u"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<document>" == xml else u"</prefecture>" 
          current_prefecture =  record.content[u"都道府県"]
          xml += u"<prefecture><name>"+MakeXML.xml_escape(current_prefecture)+u"</name>"
        xml+= u"<area>"
        xml+= u"<id>"+MakeXML.xml_escape(record.content[u"マップid英数字"])+u"</id>"
        xml+= u"<name>"+MakeXML.xml_escape(record.content[u"市区町村"])+u"</name>"
        xml+= u"<link>"+MakeXML.xml_escape(record.content[u"マップurl"])+u"</link>"
        xml+= u"<mobile_link>"+MakeXML.xml_escape(record.content[u"携帯マップurl"])+u"</mobile_link>"
        xml+= u"</area>"
      xml += u"</prefecture></document>"
      return xml


class MakeHTML:

    def make(self):
      client = gdata.spreadsheet.text_db.DatabaseClient('kyusuisho.appspot.com@gmail.com', 'ohsiusuyk')
      db = client.GetDatabases(name=u'kyusuisho.appspot.com')[0]
      html=MakeHTML.make_html(db.GetTables(name=u'root')[0])
      page = Page.gql('WHERE page_id = :1', 1).get()
      if page is None:
        page = Page(page_id=1,html=html)
      else:
        page.html = html
      page.put()

    @classmethod
    def html_escape(cls,text):
      MakeHTML.html_escape_table = {
        #  u"&": u"&amp;",
        u'"': u"&quot;",
        u"'": u"&apos;",
        u">": u"&gt;",
        u"<": u"&lt;",
      }
      return u"".join(MakeHTML.html_escape_table.get(c,c) for c in text)

    @classmethod
    def make_html(cls,table):
      html = u""
      scripts = []
      current_prefecture = u"";
      for record in table.GetRecords(1, 999999999):
        if current_prefecture != record.content[u"都道府県"]:
          html += u"" if u"" == html else u"</ul></li>" 
          current_prefecture =  record.content[u"都道府県"]
          html += u"<li>"+MakeHTML.html_escape(current_prefecture)+u"<ul>"
        html+= u'<li>'
        html+= u'<a href="'+MakeHTML.html_escape(record.content[u"携帯マップurl"])+u'"'
        html+= u' id="'+MakeHTML.html_escape(record.content[u"マップid英数字"])+u'"'
        html+= u' class="link"'
        html+= u' name="'+MakeHTML.html_escape(record.content[u"マップid英数字"])+u'">'
        html+= MakeHTML.html_escape(record.content[u"市区町村"])+u'</a></li>'
        scripts.append(u'"'+MakeHTML.html_escape(record.content[u"マップid英数字"])+u'":"'+MakeHTML.html_escape(record.content[u"マップurl"])+u'"')
      html += u'</ul></li><script type="text/javascript" id="gmaps">l={'
      html += u",".join(scripts)
      html += u'};</script>'
      return html

class MakeXMLHandler(webapp.RequestHandler):
    
    def __init__(self):
        self.application = MakeXML()
    
    def get(self):
        self.application.make()

class MakeHTMLHandler(webapp.RequestHandler):
    
    def __init__(self):
        self.application = MakeHTML()
    
    def get(self):
        self.application.make()

def main():
    application = webapp.WSGIApplication([('/crons/make_html', MakeHTMLHandler),('/crons/make_xml', MakeXMLHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
