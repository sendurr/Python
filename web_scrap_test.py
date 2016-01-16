'''##########################################################################
    Title : Course Extractor  - http://www.cortland.edu
    Author: Sendurr Selvaraj : sendurr@email.sc.edu
    Description: This script extracts the course schedule into an excel from
                 http://www.cortland.edu website
##########################################################################'''

'''##########################################################################
    Library Section: Import all libraries used in the script
##########################################################################'''
from bs4 import BeautifulSoup
import urllib2
import argparse


def get_url_content(x):
    return BeautifulSoup(open(x))

'''##########################################################################
    Main Function:
##########################################################################'''

def main():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-i","--input",help="Enter the URL")
    args = parser.parse_args()
    if args.input:
        print ("Extracting data from website: " + args.input)
        university, domain = args.input.split("@")
        print ("university:") + university
        print ("domain:") + domain
    
    
    url = "F:\work in-progress\Python\cortland_Spring_2016_Course_Schedule.html"
    
    ''' Fetch the URL content for analysing '''
    #soup = get_url_content(url)
    #print soup
    

if __name__ == "__main__":
    main()	
    print ( "MSU Complete.")
    raw_input("Enter to exit")
    sys.exit()
