'''##########################################################################
    Title : Course Extractor  - http://www.cortland.edu
    Author: Sendurr Selvaraj : sendurr@email.sc.edu
    Description: This script extracts the course schedule into an excel from
                 http://www.cortland.edu website
##########################################################################'''
from bs4 import BeautifulSoup
import urllib2
url = "F:\work in-progress\Python\cortland_Spring_2016_Course_Schedule.html"
#page=urllib2.urlopen(url)
#soup = BeautifulSoup(page.read())

soup = BeautifulSoup(open(url))
print soup.prettify()
print soup.html.body
print soup.find_all("table")