#!/usr/bin/env python
import tika
tika.initVM()
from tika import parser
import os
import re
import pandas as pd
import codecs
from bs4 import BeautifulSoup
from services.api.core import classifier

class process_file():
    def __init__(self):
        self.name = 'Process File'

    def convertFileContent(filepath):
        if os.path.isfile(filepath):
            parsed = parser.from_file(os.path.join(path, file), xmlContent=True)
            content = parsed['content']
            clean = re.compile('<.*?>')
            content = re.sub(clean, '', content)
            if content.strip() != '':
                with codecs.open(os.path.join(out_path, file+'.html'), 'w', "utf-8") as f:
                    f.write(parsed['content'])
            else:
                #get from tesseract html - get code from Rahul's team and integrate here
                pass

    def process_page_content(self, content):
        content = sorted(content, key=lambda k: k['page_no'])
        sorted_content = []
        for page in content:
            sorted_content.append(page["page_hocr"])
        return sorted_content

    def convert_file_to_pages(self):
        path = '/home/user/Shyam/Code/Release_6.0/Dev/Snorkel/predictions/For Linking/html_format/'
        files = ['1040 - SOW - SYS11-890.html', 'D00188.html', 'D00221.html', 'D00250.html', 'D00339.html', 'D00362.html', 'D00400.html', 'D00423.html', 'D00469.html', 'D00738.html', 'D00740.html', 'D00820.html', 'D00827.html', 'D00862.html', 'D00955.html', 'D01124.html', 'D01265.html', 'D01351.html', 'D01661.html', 'D01914.html', 'D01960.html', 'D02134.html', 'D02362.html', 'D02379.html', 'D02483.html', 'D02502.html', 'D02503.html', 'D02647.html', 'D02757.html', 'D02842.html', 'D03007.html', 'D03069.html', 'D03070.html', 'D03123.html', 'D03153.html', 'D03166.html', 'D03719.html', 'D03786.html', 'D03866.html', 'D04114.html', 'D04125.html', 'D04439.html', 'D04495.html', 'D04668.html', 'D04842.html', 'D08522.html']
        categories = []
        #for file in os.listdir(path):
        #for root, dirs, files in os.walk(path):
        for file in files:
            file = 'D02483.html'
            if os.path.isfile(os.path.join(path, file)):
                print(file)
                with open(os.path.join(path, file), 'r', encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    content = re.sub("<span.*?>|</span>","", content)
                    soup = BeautifulSoup(content, 'html.parser')
                    isTika = soup.find('meta', attrs= {'content': 'org.apache.tika.parser.pdf.PDFParser'})
                    if isTika is not None:
                        pages = self.processTikaFile(content)
                    else:
                        pages = self.processTesseractFile(content)
                    text = self.get_all_text_from_pages(pages)
                    doc_classifier = classifier.document_classifier(text, file)
                    result = doc_classifier.classify()
                    result.to_csv('df_latent.csv', index=False)
                    print(result)
                    #categories.append(result)

            """text = ' '.join(i for i in temp)
            # write data in a file. 
            file1 = open('../data/txt_format/'+file.split('.')[0]+'.txt','w')
            file1.write(text)
            file1.close()"""
            break

        # Write results to CSV
        #df = pd.DataFrame(categories)
        #df.to_csv('linkage_classification.csv', index=False)
        return categories

    def processTikaFile(self, content):
        pages = []
        soup = BeautifulSoup(content, 'html.parser')
        for page in soup.findAll('div', attrs = {'class':'page'}):
            paragraphs = []
            for x in page.find_all('p'):
                paragraphs.append(' '.join([x for x in str(x).split()]))
            text = ' '.join([x for x in paragraphs])
            text = '<div class="page">'+text+"</div>"
            pages.append(text)
        return pages

    def processTesseractFile(self, content):
        pages = []
        soup = BeautifulSoup(content, 'html.parser')
        VALID_TAGS = ['div', 'p']
        for page in soup.findAll('div', attrs = {'class':'ocr_page'}):
            #print(page.get('title').split('"')[1].split('-')[-1].split('.')[0])
            page_text = '<div class="page">'
            for area in page.findAll('div', attrs = {'class':'ocr_carea'}):
                text = ' '.join([x for x in area.text.split()])
                text = ' <p>' + text + '</p> '
                page_text += text
            page_text += "</div>"
            pages.append(page_text)
        return pages

    def get_all_text_from_pages(self, pages):
        text_list = []
        text = None

        try:
            for page in pages:
                soup = BeautifulSoup(page, 'html5lib')
                divpage = soup.find('div', attrs={'class': 'page'})
                text_list.append(divpage.text)
            text = " ".join(text_list)

        except Exception as ex:
            print(ex)

        return text

if __name__ == "__main__":
    processFile = process_file()
    processFile.convert_file_to_pages()