'''################################################################################
        CORTLAND PARSER
                Parses the course information from Cortland University.
                        
                Author:   Sendurr Selvaraj
                Email:    sendurr@hotmail.com
################################################################################'''

# -*- coding: UTF-8 -*-
import os, sys
import platform
import re
import urllib2
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from csv import writer

  
'''################################################################################
        PARSE HTML
                Open file and fix any html that is breaking the parsing process
################################################################################'''
def ParseHTML( data, csvWriter, year, term ):
        
        soup = BeautifulSoup( data , "html.parser")


        '''--------------------------------------------------------------------------------
                STEP ONE:    
                        Separate and iterate through each course
        --------------------------------------------------------------------------------'''
        
        courses_temp = soup.find_all( "table" )
        courses_dep = courses_temp[1].find_all("table")
        #start courses in each department

        for course in courses_dep:
                rowData         = []
                
                # need to initialize these variables so they are within the necessary scope
                name_len=0
                department = summary = name = code = remarks = section = courseNo = instructor = start_time=""
                end_time = end_day_temp = dummy = str_subdata = days = availability = ""
                
                '''--------------------------------------------------------------------------------
                        STEP TWO:    
                                Get general course information
                --------------------------------------------------------------------------------'''
                courseData = course.find_all( "tr")
                
                for index, data in enumerate( courseData ):
                        
                        #department heading condition
                        if ( index == 0 ):
                                department = data.find('h3').text
                        
                        #course summary
                        elif (data.find("td",{'bgcolor':'#e0e0e0'}) is not None):
                                name_len=0
                                summary = data.td.text
                                name = data.td.h4.text[8:]
                                code = data.td.h4.a.text
                                name_len=len(name)
                        
                        #course other info
                        elif (data.find("td",{'bgcolor':'fafae8'}) is not None):
                                remarks = data.td.text
                        
                        #course details
                        else:
                                sectionsData = data.find_all( "td" )
                                
                                for sub_index, subdata in enumerate( sectionsData ):
                                        
                                        if ( sub_index == 0 ):
                                                subdata_temp = subdata.text
                                                subdata_temp = subdata_temp.replace("->","")
                                                subdata_temp = subdata_temp.replace(u'\xa0', '').encode('utf-8')
                                                section = subdata_temp[8:11]
                                                courseNo = subdata_temp[11:]
                                        
                                        elif ( sub_index == 1 ):
                                                instructor = subdata.br.text
                                                
                                        elif ( sub_index == 2 ):
                                                x=subdata.text
                                                
                                                if (x.find("TBA") == -1):
                                                        start_time = subdata.text[0:9]
                                                        end_time  = subdata.text[13:23]
                                                        availability = subdata.br.text
                                                        avail_len=len(availability)
                                                        avail_len = len(x) - avail_len
                                                        days = x[27:avail_len]

                                                else:
                                                        start_time = end_time = days ="TBA"
                                                        availability = subdata.text[3:]


                                rowData.extend( [ department, code, name, courseNo , section, instructor ] )
                                rowData.extend( [ start_time, end_time, days, availability] )
                                csvWriter.writerow( rowData )
                                del rowData[:]
                        
                # end for-each sectionsData
        #end for-each courses'''
        
        

'''################################################################################
        FORM CRAWLER
                Crawls the form on the provided URL.
                Returns a list of web pages.
################################################################################'''
                        
def formCrawler( url, yearArg, semesterArg ):
        resultPages = []
        
        try:
                pagesource      = urllib2.urlopen( url, timeout = 8 )
                sourceData      = pagesource.read()
                
        except Exception:
                print "crawl error " + url
                exit( -1 )
                
        '''--------------------------------------------------------------------------------
                Find the appropriate semester within the form options
        --------------------------------------------------------------------------------'''
                                                                                
        siteSoup = BeautifulSoup( sourceData ,"html.parser")
        
        '''--------------------------------------------------------------------------------
                Build a list of the semesters from the options, then compare those strings
                against the semester + year that we want.
                
                The text in the semestersList is in Unicode. There is probably a better way to
                search if the text contains the year and semester we're searching for..
                I'll look into it.
        --------------------------------------------------------------------------------'''
        
        semesterList    = []
        semesterIndex   = 0
        semester_key="Term"
        semesterArg="Spring"
        yearArg="2016"
        sem_lookup ={'Spring Term 2016':'201620','Winter Term 2016':'201610','Fall Term 2015':'201590'}
        
        semesters = siteSoup.find_all("b")
           
        
        for semester in semesters:
                if semester.text.find(semester_key) != -1:
                    semesterList.append( semester.text )

        
        condition = semesterArg + " " + semester_key + " " + str(yearArg)

        '''--------------------------------------------------------------------------------
                The crawler!
                Crawls the form, adds the search result pages to our list of pages.
                
                PhantomJS crawls the pages without requiring them to be rendered, it's approx.
                40-50% faster.
                
                To use it the 'phantomjs.exe' needs to either be passed in or already in the
                system path.
        --------------------------------------------------------------------------------'''
                        
     # call phantomjs based on os
        import platform
        driverLoc=""
        if platform.system()=="Windows":
                driverLoc = os.path.dirname(os.path.abspath("__file__")) + "/phantomjs.exe"
        else:
                driverLoc = "/usr/bin/phantomjs"
        browser = webdriver.PhantomJS( driverLoc )

        browser.get( url )

        semester_value = sem_lookup[condition]
        #semester_css= BuildCSS_Sem(semester_value)
        selection = browser.find_element_by_css_selector( "[type='radio'][value='201620']" )
        selection.click()

        selection = Select( browser.find_element_by_name( "dept_code" ) )
        selection.select_by_index( 0 )

        selection = Select( browser.find_element_by_name( "subj_code" ) )
        selection.select_by_index( 0 )

        selection = Select( browser.find_element_by_name( "sec_attr" ) )
        selection.select_by_index( 0 )

        selection = Select( browser.find_element_by_name( "ptrm_code" ) )
        selection.select_by_index( 0 )

        element = browser.find_element_by_css_selector( "[type='radio'][value='All Sections']" )
        element.click()

        element=browser.find_element_by_css_selector( "[type='submit'][value='Search']" )
        element.click() 

        resultPages.append( browser.page_source )               
        browser.close()

        return resultPages
                        

'''################################################################################
        MAIN
                Executes the program
################################################################################'''
                        
def main():
        parser = argparse.ArgumentParser()
        
        # URL
        parser.add_argument(
                                        '-i', 
                                        action = 'store', 
                                        dest = 'url',
                                        help = 'url of main page of class schedule', 
                                        default = 'http://studentinfo.cortland.edu/pls/prod/regweb.course_sched'
                                        )
        
        # OUTPUT FILENAME
        parser.add_argument(
                                        '-o', 
                                        action = 'store', 
                                        dest = 'ofile', 
                                        default = "cortland.csv",
                                        help = 'output csv file: msu.csv'
                                        )
        
        # YEAR
        parser.add_argument(
                                        '-y', 
                                        action = 'store', 
                                        dest = 'year', 
                                        default = 2015,
                                        help='year of the semester'
                                        )
        
        # SEMESTER
        parser.add_argument(
                                        '-t', 
                                        action = 'store', 
                                        dest = 'semester', 
                                        default = "Spring",
                                        help = 'semester'
                                        )                                                       
        
        parser.add_argument(
                                        "-v", 
                                        "--verbosity", 
                                        action = "count", 
                                        default = 0
                                        )
        
        parser.add_argument(
                                        '--version', 
                                        action = 'version', 
                                        version = '%(prog)s 1.0'
                                        )
        
        args = parser.parse_args()

        '''--------------------------------------------------------------------------------
                Build the file name from the arguments.
                Prepare the csv file and the csv writer.
                Crawl the forms.
                Go through the list pageResults repairing and parsing the web data.
        --------------------------------------------------------------------------------'''
        
        university, extension = args.ofile.split(".")
        outFilename=args.ofile

        
        csvFile         = open( outFilename, "wb" )
        csvWriter       = writer( csvFile, lineterminator = '\n' )
                
        csvWriter.writerow( ["Department","Code","Name","Number","Section","Instructor",
                             "Start Time","End Time","Days","Availability"
                            ] )

        pageResults = formCrawler( args.url, args.year, args.semester )

        for page in pageResults:
                ParseHTML( page, csvWriter, args.year, args.semester )

                
        csvFile.close()


'''#############################################################################'''
                
if __name__ == "__main__":
        main()  

        print ( "Cortland Extract Complete.")        
        sys.exit()
