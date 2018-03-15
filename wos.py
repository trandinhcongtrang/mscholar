#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'jonathansitruk'
__author2__ = 'trangtran: '
'''
Improved: 
1. login function
2. Use ChromeDriver for stability
'''
import optparse
import json
import bibtexparser
import scrapy
from selenium.webdriver.common.keys import Keys
from scrapy import Selector
from scrapy.spiders import Spider
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os.path
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import os
from random import randint
import errno
import sys
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

start_urls = [
    "http://apps.webofknowledge.com.inshs.bib.cnrs.fr/"
    #"https://bib.cnrs.fr/home/"
    #"http://apps.webofknowledge.com.doc-distant.univ-lille2.fr/WOS_AdvancedSearch_input.do?SID=Z25LwlVoDfz7JfgLe3M&product=WOS&search_mode=AdvancedSearch"
    #"http://webofknowledge.com.doc-distant.univ-lille2.fr/"
]

# scrapy crawl webby
# C:\Python27\Scripts\Scrapy.exe crawl tan
# cd C:\Users\sitruk\Dropbox\Crawler\Scrapy\webscience\webscience\spiders

class Crawler(Spider):
    name = "tan"
    handle_httpstatus_list = [200, 404]

    def __init__(self, url, sleep, instance):
        self.__login_page__ = url
        self.__sleep_time__ = sleep
        self.__instance__ = instance

        current_path = os.path.dirname(os.path.realpath(__file__))
        chrome = os.path.join(current_path, 'chromedriver')

        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : os.path.join(current_path, 'instance%d' % (instance), 'downloads')}
        chromeOptions.add_experimental_option("prefs",prefs)

        self.driver = webdriver.Chrome(executable_path=chrome, chrome_options=chromeOptions)
        #self.driver.implicitly_wait(2)
        self.driver.implicitly_wait(5);
    
    def sleep(self):
        time.sleep(self.__sleep_time__)

    def move(self, src, dst):
        if src is not None:
            os.popen('mv instance%d/downloads/%s instance%d/downloads/%s' % (self.__instance__, src, self.__instance__, dst))
        else:
            with open(os.path.join('instance%d/downloads' % self.__instance__, dst), 'w'):
                pass
    def write(self, config):
        with open('instance%d/config.txt' % self.__instance__, 'w') as cfg:
            json.dump(config, cfg)
            cfg.flush()

    def login1(self):
        self.driver.get(self.__login_page__)
        
        # Sleep amount
        sleep = 5
        if self.__login_page__:
            self.driver.find_element_by_id("userIdPSelection_iddtext").click()   
            self.driver.find_element_by_id("userIdPSelection_iddtext").send_keys(u"Université Lille 2: Droit et Santé")   
                    
            self.driver.find_element_by_name("Select").click()
            self.sleep()

            self.driver.find_element_by_id("username").clear()
            self.driver.find_element_by_id("username").send_keys("ludovic.dibiaggio") # HE
            self.driver.find_element_by_id("password").clear()
            self.driver.find_element_by_id("password").send_keys("3cmbfnoe") # HERE

            self.driver.find_element_by_name("submit").click()

            self.sleep()
            return "OK"
        else:
            return None

    def login_portal(self):
        self.driver.get(self.__login_page__)
        
        if self.__login_page__:
            #
            # self.driver.find_element_by_xpath('//*[@id="ebsco_widget"]/div/div/div/div/nav/div/ul/div[2]/div/button').click()

            # Click login old portal
            self.driver.find_element_by_xpath('//*[@id="bibapi_toggle"]').click()
            self.sleep()

            username = self.driver.find_element_by_xpath('//*[@id="username"]')
            username.send_keys('16SOCUMR7321')

            password = self.driver.find_element_by_xpath('//*[@id="password"]')
            password.send_keys('7UU2G6')
            self.driver.find_element_by_xpath('//*[@id="bibapi-panel"]/div/form/div[4]/button').click()
            self.sleep()

            # Click A database
            #self.driver.find_element_by_xpath('//*[@id="ebsco_widget"]/div/div/div/div/nav/div/ul/li[3]/a').click()
            #self.sleep()

            # Select WOS Core Collection
            #self.driver.find_element_by_xpath('//*[@id="ebsco_widget"]/div/div/div/div/span/div/ul/li[17]/ul/li[2]').click()
            #self.sleep()

            # Close the login window
            #self.driver.close()

            #Switch to wos window
            #self.driver.switch_to_window(self.driver.window_handles[0])
            #print self.driver.window_handles
            #self.driver.switch_to_window(self.driver.window_handles[-1])
            
            return "OK"
        else:
            return None
    
    
    def parse_year(self, config, complete):
        # Go to the advanced search menu by 1) clicking on the dropdown, 2) clicking on the advanced search option
        #self.driver.find_element_by_xpath('//i[@class="icon-dd-active-block-search"]').click()
        self.driver.find_element_by_xpath('/html/body/div[7]/div/ul/li[3]/a').click()
        #self.driver.find_element_by_xpath('//i[@class="icon-dd-active-block-search"]/ul/li[5]/a').click()

        # Selecting "From box"
        print 'Selecting From box'
        self.driver.find_element_by_xpath('//*[@id="periodRange"]').click()
        
        # Selecting From year
        print 'Selecting From year'
        self.driver.find_element_by_xpath('//*[@id="s2id_autogen3"]').click()
        self.driver.find_element_by_xpath('//*[@id="select2-results-4"]/li[%d]/div' % (config['year'] - 1899)).click()

        # Selecting to year: 2017: label-371, 1991: label-397
        print 'Selecting to year'
        self.driver.find_element_by_xpath('//*[@id="s2id_autogen5"]').click()
        self.driver.find_element_by_xpath('//*[@id="select2-results-6"]/li[%d]/div' % (2018 - config['year'])).click()

        # Set address if any
        if config['address']:
            input = self.driver.find_element_by_id("value(input1)")
            input.clear()
            input.send_keys('AD=(%s)' % config['address'])
                    # submit button location
        self.driver.find_element_by_id("searchButton").click()
        # Click on results
        self.driver.find_element_by_id('set_1_div').click()
        first = 1
        if first == 1:
            # Click on pages settings
            self.driver.find_element_by_xpath('//div[@id="s2id_selectPageSize_.bottom"]').click()
            # Chose 50 results per page
            self.driver.find_element_by_xpath('//ul[@class="select2-results"]/li[3]/div').click()
            first = 0

        articles = self.driver.find_element_by_id('hitCount.top')
        pages = self.driver.find_element_by_id('pageCount.top')
        print 'Found %d articles' % int(articles.text.replace(',', ''))
        print 'Found %d pages' % int(pages.text.replace(',', ''))
        try:
            page_start = config['page']
        except Exception as e:
            page_start = 1
        for p in range(page_start, int(pages.text.replace(',', ''))):
            #
            print 'Go to page#%d' % p
            page_input = self.driver.find_element_by_xpath('//*[@id="summary_navigation"]/table/tbody/tr/td[2]/input')
            page_input.clear()
            page_input.send_keys('%s' % p)
            page_input.send_keys(Keys.RETURN)

            # Click to format
            self.driver.find_element_by_xpath('//div[@id="s2id_saveToMenu"]/a/span[2]/b').click()
            # Select save to orther format
            self.driver.find_element_by_xpath('//select[@id="saveToMenu"]/option[5]').click()
            
            #Choose bibtex
            self.driver.find_element_by_xpath('//*[@id="ui-id-7"]/form/div[3]/div/div').click()
            self.driver.find_element_by_xpath('//*[@id="saveOptions"]/option[2]').click()

            # Choose all detail
            self.driver.find_element_by_xpath('//*[@id="ui-id-7"]/form/div[2]/div[2]').click()
            self.driver.find_element_by_xpath('//*[@id="bib_fields:fullrec_fields_option"]').click()

            # Send result
            self.driver.find_element_by_xpath('//*[@id="ui-id-7"]/form/div[4]/span').click()
            self.sleep()
            
            # Press Close
            self.driver.find_element_by_xpath('//*[@id="ui-id-7"]/form/div[2]/a').click()
            # Click to format
            self.driver.find_element_by_xpath('//div[@id="s2id_saveToMenu"]/a/span[2]/b').click()

            # Save the current result to another file
            fs = 'bibtex%s%spage%d.bib'
            year = '_year_%s_' % config['year']
            if config['address'] is not None:
                address = '_address_%s_' % config['address']
            else:
                address = ''
            result_file = fs % (year, address, p)
            print 'Copying result (savedrecs) to %s' % result_file
            self.move("savedrecs.bib", result_file)
            #os.popen('mv bibtex/savedrecs.bib bibtex/%s' % (result_file))
            
            config['page'] = p + 1
            self.write(config)

        # Repeat
        print "END"
        complete = True
        #self.driver.close()

    def parse_title(self, inputfile, config, complete):
        with open(inputfile) as f:
            lines = f.readlines()
        lines = [x.strip() for x in lines] 

        self.sleep()
        first = 1
        
        for (i, line) in enumerate(lines):
            if (i < config['skip']):
                continue
            if (i > config['max']):
                print 'Reach line %d, programe terminate by configuration' % i
                break

            # For each line
            # appln_id|year|pat_publn_id|npl_publn_id|npl_type|npl_biblio|npl_citn_seq_nr|title|journal|publisher|I|subfield|field|domain
            terms = line.split('|')
            paper_id = terms[3]
            if os.path.isfile('instance%s/downloads/%s.bib' % (self.__instance__, paper_id)):
                continue

            paper_title = (re.sub('\W+', ' ', terms[7])).lower()
            word_tokens = word_tokenize(paper_title)
            filtered_sentence = [w for w in word_tokens if not w in stop_words]
            #print "filtered_sentence = "
            #print filtered_sentence
            if len(filtered_sentence[0]) <3:
                filtered_querry = "%s*" % " ".join(filtered_sentence)
            else:
                filtered_querry = "*%s*" % " ".join(filtered_sentence)
            #print paper_title
            
            querries = ["\"%s\"" % paper_title, filtered_querry]

            for querry in querries:
                print querry
                try:
                    if (i % 100) == 0:
                        # Clear search history
                        self.driver.find_element_by_xpath('//*[@id="skip-to-navigation"]/ul[2]/li[2]/a').click()

                        # Select all
                        self.driver.find_element_by_xpath('/html/body/div[1]/div[25]/form/table/tbody/tr[1]/th[6]/div[2]/input[1]').click()

                        # Delete all
                        self.driver.find_element_by_xpath('/html/body/div[1]/div[25]/form/table/tbody/tr[1]/th[6]/div[2]/input[2]').click()
                except Exception as exc:
                    pass
                while True:
                    try:
                        # Do Basic search
                        search = self.driver.find_element_by_xpath('//*[@id="value(input1)"]')
                        search.clear()
                        search.send_keys('%s' % paper_title)
                
                        # Click Search Button
                        self.driver.find_element_by_xpath('//*[@id="WOS_GeneralSearch_input_form_sb"]').click()
                        break
                    except Exception as exc:
                        self.driver.get("http://apps.webofknowledge.com.inshs.bib.cnrs.fr/")

                # try select pages
                try:
                    # Select All pages
                    #self.driver.find_element_by_xpath('//div[@class="page-options-inner-left"]/ul/li[1]/input').click()
                    self.driver.find_element_by_xpath('//*[@id="page"]/div[1]/div[25]/div[2]/div/div/div/div[2]/div[3]/div[2]/div/div/div/div[1]/ul/li[1]/input').click()

                    # Click to format arrow
                    self.driver.find_element_by_xpath('//*[@id="page"]/div[1]/div[25]/div[2]/div/div/div/div[2]/div[3]/div[2]/div/div/div/div[1]/ul/li[3]/div/span/span/span[1]/span/span[2]').click()
                    # Select save to orther format
                    self.driver.find_element_by_xpath('//*[@id="select2-saveToMenu-results"]/li[5]').click()
                    
                    # Click Record Content
                    self.driver.find_element_by_xpath('//*[@id="select2-bib_fields-container"]').click()
                    self.driver.find_element_by_xpath('//*[@id="select2-bib_fields-results"]/li[4]').click()

                    # Click File Format
                    self.driver.find_element_by_xpath('//*[@id="saveOptions"]').click()
                    # click bibtex
                    self.driver.find_element_by_xpath('//*[@id="saveOptions"]/option[2]').click()

                    # Send result
                    self.driver.find_element_by_xpath('//*[@id="ui-id-7"]/form/div[4]/span/input').click()
                    self.sleep()
                    
                    # Press Close
                    self.driver.find_element_by_xpath('//*[@id="page"]/div[9]/div[1]/button').click()

                    # Save the current result to another file
                    result_file = '%s.bib' % paper_id
                    print 'Copying result (savedrecs) to %s' % result_file
                    self.move("savedrecs.bib", result_file)
                    if os.path.isfile('instance%s/downloads/%s.notfound' % (self.__instance__, paper_id)):
                        os.popen('rm -f instance%s/downloads/%s.notfound' % (self.__instance__, paper_id))
                    # Break out of querries
                    #self.driver.get("http://apps.webofknowledge.com.inshs.bib.cnrs.fr/")
                    self.driver.execute_script("window.history.go(-1)")
                    break
                    # Delete search history
                    #self.driver.find_element_by_xpath('/html/body/div[1]/div[25]/form/table/tbody/tr[1]/th[6]/div[2]/input[1]').click()
                    #self.driver.find_element_by_xpath('/html/body/div[1]/div[25]/form/table/tbody/tr[1]/th[6]/div[2]/input[2]').click()

                except Exception as exp:
                    #print exp
                    print 'title not found'
                    self.move(None, "%s.notfound" % paper_id)
                    #self.driver.get("http://apps.webofknowledge.com.inshs.bib.cnrs.fr/")

            print ' line %d done' % i
            config['skip'] = i
            self.write(config)
            # Navigate back to Basic Search
            
        # end for (i, line) in enumerate(lines):

        # Repeat
        print "END"
        complete = True
        #self.driver.close()

    def parse(self, inputfile, config, complete):

        with open(inputfile) as f:
            lines = f.readlines()
        lines = [x.strip() for x in lines] 

        self.sleep()
        first = 1
        # Go to the advanced search menu by 1) clicking on the dropdown, 2) clicking on the advanced search option
        #drop = self.driver.find_element_by_xpath('//i[@class="icon-dd-active-block-search"]')
        #drop.click()

        search = self.driver.find_element_by_xpath('/html/body/div[7]/div/ul/li[3]/a')
        search.click()
        
        self.sleep()

        for (i, line) in enumerate(lines):
            if (i < config['skip']):
                continue
            if (i > config['max']):
                print 'Reach line %d, programe terminate by configuration' % i
                break

            # For each line
            # Add the new search by category[n] by first clearing the search field
            input1 = self.driver.find_element_by_id("value(input1)")
            input1.clear()
            input1.send_keys(line)

            # submit button location
            self.driver.find_element_by_id("searchButton").click()

            # Click on results
            self.driver.find_element_by_id('set_1_div').click()

            if first == 1:
                # Click on pages settings
                self.driver.find_element_by_xpath('//div[@id="s2id_selectPageSize_.bottom"]').click()

                # Chose 50 results per page
                self.driver.find_element_by_xpath('//ul[@class="select2-results"]/li[3]/div').click()
                
                first = 0
     
            # Select All pages
            self.driver.find_element_by_xpath('//div[@class="page-options-inner-left"]/ul/li[1]/input').click()

            # Click to format
            self.driver.find_element_by_xpath('//div[@id="s2id_saveToMenu"]/a/span[2]/b').click()
            # Select save to orther format
            self.driver.find_element_by_xpath('//select[@id="saveToMenu"]/option[5]').click()
            
            #Choose bibtex
            self.driver.find_element_by_xpath('//*[@id="ui-id-7"]/form/div[3]/div/div').click()
            self.driver.find_element_by_xpath('//*[@id="saveOptions"]/option[2]').click()

            # Choose all detail
            self.driver.find_element_by_xpath('//*[@id="ui-id-7"]/form/div[2]/div[2]').click()
            self.driver.find_element_by_xpath('//*[@id="bib_fields:fullrec_fields_option"]').click()

            # Send result
            self.driver.find_element_by_xpath('//*[@id="ui-id-7"]/form/div[4]/span').click()
            self.sleep()
            
            # Press Close
            self.driver.find_element_by_xpath('//*[@id="ui-id-7"]/form/div[2]/a').click()

            # Save the current result to another file
            date = os.popen('date +%F-%H-%M-%S').read().strip()
            print date
            print 'Copying result (savedrecs) to bibtex_line_%d ' % i
            os.popen('mv bibtex/savedrecs.bib bibtex/bibtex_line_%d' % i)
            
            print 'Got line %d' % i
            config['skip'] = i
            self.write(config)
            # Navigate back to AdvancedSearch
            self.driver.get("http://apps.webofknowledge.com.doc-distant.univ-lille2.fr/WOS_AdvancedSearch_input.do?product=WOS&search_mode=AdvancedSearch&replaceSetId=&goToPageLoc=SearchHistoryTableBanner&SID=R2JxcxoJnkQClmsLPVn&errorQid=1#SearchHistoryTableBanner")

            # Delete search history
            self.driver.find_element_by_xpath('/html/body/div[1]/div[25]/form/table/tbody/tr[1]/th[6]/div[2]/input[1]').click()
            self.driver.find_element_by_xpath('/html/body/div[1]/div[25]/form/table/tbody/tr[1]/th[6]/div[2]/input[2]').click()

        # Repeat
        print "END"
        complete = True
        self.driver.close()

class Sample:
  url = ""

if __name__ == '__main__':
    usage = '$ ./wos.py -f INPUT_FILE\n --year YEAR\n --address ADDRESS \n -f INPUT_FILE --title'
    fmt = optparse.IndentedHelpFormatter(max_help_position=50, width=100)
    parser = optparse.OptionParser(usage=usage, formatter=fmt)
    group = optparse.OptionGroup(parser, 'Personal Customs')
    group.add_option('-i', '--skip', type='int', default=None,
                     help='skip to line n')
    group.add_option('-m', '--max', type='int', default=None,
                     help='max to line n')
    group.add_option('-y', '--year', type='int', default=None,
                     help='Get data from year ')
    group.add_option('-A', '--address', type='str', default=None,
                     help='Get data from address ')
    group.add_option('-t', '--title', action='store_true', default=False,
                     help='Get data from title ')
    group.add_option('-f', '--file', dest='input', default=None,
                    help="write report to FILE", metavar="FILE")
    group.add_option('-n', '--instance', type='int', default=None,
                    help='Run instance n')
    group.add_option('-a', '--restart', action='store_true', default=False,
                     help='Auto restart chrome driver when failed')
    parser.add_option_group(group)

    options, _ = parser.parse_args()
    if (not options.input and not options.year) or not options.instance:   # if filename is not given
        parser.error('Filename not given: $ ./wos.py -f INPUT_FILE --instance NUMBER')
        sys.exit(1)

    restart = False
    if options.restart:
        restart = True
    
    # Load configurations from file or from settings
    config = {}
    os.popen('mkdir -p instance%d/downloads' % options.instance)
    try:
        with open('instance%d/config.txt' % options.instance, 'r') as cfg:
            config = json.load(cfg)
    except (IOError, ValueError) as e:
        config = {'skip': 1, 'max':999999999, 'page':1}
        with open('instance%d/config.txt' % options.instance, 'w') as cfg:
            json.dump(config, cfg)
    
    if options.skip is not None:
        config['skip'] = options.skip
    if options.max is not None:
        config['max'] = options.max
    if options.year is not None:
        if (options.year) > 2017 or options.year < 1991:
            print 'Allowed --year option from 1991 to 2017'
            exit(0)
        config['year'] = options.year
    if options.address is not None:
        config['address'] = options.address

    complete = False
    failed_line = 0

    while True:
        #print 'Back up current bibtex'
        #date = os.popen('date +%F-%H-%M').read().strip()
        #print 'Back up current savedrecs.bib if any'
        #os.popen('mkdir -p bibtexbk')
        #os.popen('cp -f bibtex/* bibtexbk/')
        #os.popen('tar czf bibtexbk.tar.gz bibtexbk')
        #os.popen('rm -f bibtex/savedrecs.bib')

        try:
            crawler = Crawler(start_urls[0], 5, options.instance)
            print 'login'
            if crawler.login_portal() is not None:
                print 'login done'
                if options.year:
                    print 'Parse data from year %d' % config['year']
                    crawler.parse_year(config, complete)
                elif options.title is True:
                    print 'Get data from WoS by title'
                    crawler.parse_title(options.input, config, complete)
                else:
                    crawler.parse(options.input, config, complete)
            crawler.driver.close()
        except Exception as exp:
            print exp
            print 'Failed at line %d' %config['skip']
            if failed_line == config['skip']:
                print 'Failed consecutively, Abort!!!!'
                restart = False
            else:
                failed_line = config['skip']
            print 'Closing chromedriver'
            crawler.driver.close()
        if complete is True:
            break
        if restart is False:
            break
        print 'Sleeping 10s..........'
        time.sleep(30)
