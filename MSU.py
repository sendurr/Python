

'''################################################################################
	MSU PARSER
		Parses the course information from Michigan State University.
			
		Author:   Matthew Robert Short
		Email:    matthew.rob.short@gmail.com
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
	REPAIR HTML
		Open file and remove invalid HTML
################################################################################'''

def RepairHTML( data ):
	data = data.replace( "</THD>", "" )


'''################################################################################
	PARSE HTML
		Open file and fix any html that is breaking the parsing process
################################################################################'''
	
def ParseHTML( data, csvWriter, year, term ):
	
	soup = BeautifulSoup( data )
	
	'''--------------------------------------------------------------------------------
		STEP ONE:    
			Separate and iterate through each course
	--------------------------------------------------------------------------------'''
	
	courses = soup.find_all( "table" )
	
	#start for-each courses
	for course in courses:
		rowData         = []
		
		# need to initialize these variables so they are within the necessary scope
		subject = courseNo = name = section = category = days = weekFreq = startWeek = \
		time = loc = instructor = credit = maxSeat = openSeat = session = email=endWeek="" \
		
		'''--------------------------------------------------------------------------------
			STEP TWO:    
				Get general course information
		--------------------------------------------------------------------------------'''
		
		courseData = course.find_all( "td", "row_Header" )
		
		for index, data in enumerate( courseData ):
			if ( index == 0 ):
				subject = data.text.encode('latin1')
				subject, courseNo = subject.replace(' ', '').split('\xa0',1)
				courseNo = courseNo.replace('\xa0','')
				
			else:				
				name = data.text.encode('latin1')
				name = name.replace('\xa0','')
				break;
		
		'''--------------------------------------------------------------------------------
			STEP THREE:    
				Separate and iterate through each section
		--------------------------------------------------------------------------------'''
		
		sectionsData = course.find_all( "tr", "row_Section" )
		
		# start for-each sectionsData
		for sectionData in sectionsData:
			condition = sectionData.find( "td", "row_SectionLite" )
			
			'''--------------------------------------------------------------------------------
				CONDITION STEP:    
					If condition is None then we have a new Section.
					
					With a new Section we want to clear the old Section data 
					and the old additionalInfo data.
					
					Otherwise we only want to clear the additionalInfo
			--------------------------------------------------------------------------------'''
			
			if condition is None:
				section 	= sectionData.find( attrs={"headers" : "Section"} ).text.strip()
				category	= ""
				credit  	= sectionData.find( attrs={"headers" : "Credits"} ).text.strip() 
				credit		= re.sub( '\D', '', credit);
				
				enrolled 	= sectionData.find( attrs={"headers" : "Enrolled"} ).text.strip()
				maxSeat    	= sectionData.find( attrs={"headers" : "Limit"} ).text.strip() 				
				openSeat 	= int( maxSeat ) - int( enrolled )
					
			'''--------------------------------------------------------------------------------
				STEP FOUR:    
					After clearing the appropriate lists we build the additionalInfo list
					with new information
			--------------------------------------------------------------------------------'''
					
			days        = sectionData.find( attrs={"headers" : "Days"} ).text.strip() 
			days 		= days.replace("Th", "H")
			days 		= days.replace("Tu", "T")
			
			time       	= sectionData.find( attrs={"headers" : "Times" } ).text.strip() 
			loc		    = sectionData.find( attrs={"headers" : "Building" } ).text.strip() 
			instructor  = sectionData.find( attrs={"headers" : "Instructor" } ).text.strip()
			session		= ""
			startWeek	= "1"
			weekFreq	= "1"
			email=""
			endWeek=""
			
			'''--------------------------------------------------------------------------------
				STEP FIVE:    
					Build the rowData list from each part of the data
			--------------------------------------------------------------------------------'''
			courseNo=courseNo.strip();
			subject=subject.strip();
			name=name.strip();
			rowData.extend( [ year, term, subject, courseNo, name, section, category, days, weekFreq ] )
			rowData.extend( [ startWeek, time, loc, instructor, credit, maxSeat, openSeat, session,email,endWeek] )
			
			csvWriter.writerow( rowData )
				
			del rowData[:]
			
		# end for-each sectionsData
	#end for-each courses
		
'''################################################################################
	FORM CRAWLER
		Crawls the form on the provided URL.
		Returns a list of web pages.
################################################################################'''
			
def formCrawler( url, yearArg, semesterArg ):
	resultPages = []
	
	try:
		pagesource 	= urllib2.urlopen( url, timeout = 8 )
		sourceData 	= pagesource.read()
		
	except Exception:
		print "crawl error " + url
		exit( -1 )
		
	'''--------------------------------------------------------------------------------
		Find the appropriate semester within the form options
	--------------------------------------------------------------------------------'''
										
	siteSoup = BeautifulSoup( sourceData )
	
	'''--------------------------------------------------------------------------------
		Build a list of the semesters from the options, then compare those strings
		against the semester + year that we want.
		
		The text in the semestersList is in Unicode. There is probably a better way to
		search if the text contains the year and semester we're searching for..
		I'll look into it.
	--------------------------------------------------------------------------------'''
	
	semesterList	= []
	semesterIndex	= 0
	
	semesters 		= siteSoup.find( "select", attrs = { "id" : "Semester" } ).find_all("option")
	deptLength		= len( siteSoup.find( "select", attrs = { "id" : "Subject" } ).find_all("option") )
	
	for semester in semesters:
		semesterList.append( semester.text )
		
	condition = semesterArg + " " + str(yearArg)
	
	for index, value in enumerate( semesterList ):
		if value.upper() == condition.upper():
			semesterIndex = index
			del semesterList[:]

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
		driverLoc = os.path.dirname(os.path.abspath(__file__)) + "/phantomjs.exe"
	else:
		driverLoc = "/usr/bin/phantomjs"
	browser = webdriver.PhantomJS( driverLoc )
	
	for index in range(0, deptLength):
		browser.get( url )
		
		selection = Select( browser.find_element_by_id( "Semester" ) )
		selection.select_by_index( semesterIndex )
		
		selection = Select( browser.find_element_by_id( "Subject" ) )
		selection.select_by_index( index )
		
		element = browser.find_element_by_id("AllOnePage")
		element.click()
		
		element.submit()
		
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
					default = 'http://schedule.msu.edu/default.asp'
					)
	
	# OUTPUT FILENAME
	parser.add_argument(
					'-o', 
					action = 'store', 
					dest = 'ofile', 
					default = "msu.csv",
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
	# outFilename = university + "_" + str( args.year ) + "_" + str( args.semester ) + "." + extension
	outFilename=args.ofile
	
	csvFile 	= open( outFilename, "wb" )
	csvWriter 	= writer( csvFile, lineterminator = '\n' )
		
	csvWriter.writerow( [
						"year", "term", "subject", "courseno", "name", "section", 
						"category", "days", "weekfreq", "startweek", "time", 
						"location", "instructor", "credit", "maxseat",
						"openseat", "session","email","endweek" 
						] )

	pageResults = formCrawler( args.url, args.year, args.semester )	
		
	for page in pageResults:
		RepairHTML( page )
		ParseHTML( page, csvWriter, args.year, args.semester )
		
	csvFile.close()


'''#############################################################################'''
		
if __name__ == "__main__":
	main()	

	print ( "MSU Complete.")	
	sys.exit()

