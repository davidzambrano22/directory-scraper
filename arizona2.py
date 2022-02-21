# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 10:04:37 2022

@author: Andres
"""
import requests
import re
import argparse
import sys
import time

def download(url, num_retries = 2, user_agent = 'wswp'):
    print('downloading', url)
    headers = {'User-agent' : user_agent}
    try:
        resp = requests.get(url, headers = headers)
        html = resp.text
        if resp.status_code >= 400:
            print('Error: status code > 400')
            html = None
            if num_retries and 500 <= resp.status_code > 600:
                return download(url, num_retries - 1)
    except requests.exceptions.RequestException as e:
        print('Download error:', e.reason)
        html = None
    return html
    
# =============================================================================
# def get_names(html):
#     links_regex = re.compile(
#         """<div class=["']views-row views-row-.*[\n\t]*.*[\n\t]*.*[\n\t]?.*<h3>(.*)<""",
#                                                       re.IGNORECASE)
#     return links_regex.findall(html)
# =============================================================================
        
        
def get_emails(html):
    email_regex = re.compile(
        """<div class=["']views-row views-row-.*[\n\t]*.*[\n\t]*.*[\n\t]?.*<h3>.*</h3>[\n\t]*.*[\n\t]*</div>[\t\n]*<div>[\n\t]*.*[\n]*.*<div>[\n]*.*""",
                                                      re.IGNORECASE)
    return email_regex.findall(html)

def get_info(html):
    """This is the Crawler"""
    mails = []
    
    if not get_emails(html):
        return None
    else:
        try:
            for cd in get_emails(html):
                if re.search('mailto:', cd):
                    name = re.findall('<h3>(.*)?<', cd)[0]
                    email = re.findall('mailto:([a-zA-Z0-9._+-]*@[a-zA-Z0-9._+-]*)', cd)[0]
                    mails.extend([name, email])
            return mails
                
        except IndexError:
            print('No hay mail')
            
def main(names, output, scheme_netloc= 'https://directory.arizona.edu/phonebook', delay = 3):
    with open(names) as names:
        names = names.read().split(',')
        print(names)
        for name in names:
            name = name.lower()
            query = '?cn={}&type=&lastname=&firstname=&email=&phone=&attribute_7='.format(name.lower())
            page_query_format = '&page='
            main_page = scheme_netloc + query
            pages = [main_page]
            page = 1
            info = True
            while pages:
                url = pages.pop()
                html = download(url)
                info = get_info(html)
                if not info:
                    break
                print(info, file = output)
                page_query_format = '&page={}'.format(page)
                next_page = scheme_netloc + query + page_query_format
                pages.append(next_page)
                page += 1
                time.sleep(delay)    
            
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n',
                        type = str, help = 'name to find')
    parser.add_argument('-o', help = 'output-file', type = argparse.FileType('w'),
                       default = sys.stdout)
    args = parser.parse_args()
    main(args.n, args.o)


    
    
