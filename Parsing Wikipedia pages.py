import requests
from bs4 import BeautifulSoup
import os
import sys
import bz2
import subprocess
import xml.sax
from keras.utils import get_file
import mwparserfromhell 
import gc
from multiprocessing import Pool 
from timeit import default_timer as timer
import json
import re

base_url = 'https://dumps.wikimedia.org/enwiki/'
index = requests.get(base_url).text
soup_index = BeautifulSoup(index, 'html.parser')

# Find the links that are dates of dumps
dumps = [a['href'] for a in soup_index.find_all('a') if 
		 a.has_attr('href')]
dumps

dump_url = base_url + '20180901/'

# Retrieve the html
dump_html = requests.get(dump_url).text

# Convert to a soup
soup_dump = BeautifulSoup(dump_html, 'html.parser')

# Find li elements with the class file
soup_dump.find_all('li', {'class': 'file'}, limit = 10)[:4]


files = []

# Search through all files
for file in soup_dump.find_all('li', {'class': 'file'}):
	text = file.text
	# Select the relevant files
	if 'pages-articles' in text:
		files.append((text.split()[0], text.split()[1:]))
		
files_to_download = [file[0] for file in files if '.xml-p' in file[0]]

keras_home='C:/Users/raksh/Desktop/Fall 2018/Big Data-Nick brown/Big-Data-Intelligence-and-Analytics-/Recommendation System for Wikipedia/Data/'

data_paths = []
file_info = []

# Iterate through each file
for file in files_to_download:
	path = keras_home+file
	
	# Check to see if the path exists (if the file is already downloaded)
	if not os.path.exists(file):
		print('Downloading')
		# If not, download the file
		data_paths.append(get_file(path, dump_url+'/'+file))
		# Find the file size in MB
		file_size = os.stat(path).st_size / 1e6
		
		# Find the number of articles
		file_articles = int(file.split('p')[-1].split('.')[-2]) - int(file.split('p')[-2])
		file_info.append((file, file_size, file_articles))
		
	# If the file is already downloaded find some information
	else:
		data_paths.append(path)
		# Find the file size in MB
		file_size = os.stat(path).st_size / 1e6
		
		# Find the number of articles
		file_number = int(file.split('p')[-1].split('.')[-2]) - int(file.split('p')[-2])
		file_info.append((file.split('-')[-1], file_size, file_number))


sorted(file_info, key = lambda x: x[1], reverse = True)[:5]

sorted(file_info, key = lambda x: x[2], reverse = True)[:5]

print(f'There are {len(file_info)} partitions.')

def process_article(title, text, timestamp, template = 'Infobox book'):
	"""Process a wikipedia article looking for template"""
	
	# Create a parsing object
	wikicode = mwparserfromhell.parse(text)
	
	# Search through templates for the template
	matches = wikicode.filter_templates(matches = template)
	
	# Filter out errant matches
	matches = [x for x in matches if x.name.strip_code().strip().lower() == template.lower()]
	
	if len(matches) >= 1:
		# template_name = matches[0].name.strip_code().strip()

		# Extract information from infobox
		properties = {param.name.strip_code().strip(): param.value.strip_code().strip() 
					  for param in matches[0].params
					  if param.value.strip_code().strip()}

		# Extract internal wikilinks
		wikilinks = [x.title.strip_code().strip() for x in wikicode.filter_wikilinks()]

		# Extract external links
		exlinks = [x.url.strip_code().strip() for x in wikicode.filter_external_links()]

		# Find approximate length of article
		text_length = len(wikicode.strip_code().strip())

		return (title, properties, wikilinks, exlinks, timestamp, text_length)



class WikiXmlHandler(xml.sax.handler.ContentHandler):
	"""Parse through XML data using SAX"""
	def __init__(self):
		xml.sax.handler.ContentHandler.__init__(self)
		self._buffer = None
		self._values = {}
		self._current_tag = None
		self._books = []
		self._article_count = 0
		self._non_matches = []

	def characters(self, content):
		"""Characters between opening and closing tags"""
		if self._current_tag:
			self._buffer.append(content)

	def startElement(self, name, attrs):
		"""Opening tag of element"""
		if name in ('title', 'text', 'timestamp'):
			self._current_tag = name
			self._buffer = []

	def endElement(self, name):
		"""Closing tag of element"""
		if name == self._current_tag:
			self._values[name] = ' '.join(self._buffer)

		if name == 'page':
			self._article_count += 1
			# Search through the page to see if the page is a book
			book = process_article(**self._values, template = 'Infobox book')
			# Append to the list of books
			if book:
				self._books.append(book)

# Object for handling xml
handler = WikiXmlHandler()

# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

def find_books(data_path, limit = None, save = True):
	"""Find all the book articles from a compressed wikipedia XML dump.
	   `limit` is an optional argument to only return a set number of books.
		If save, books are saved to partition directory based on file name"""

	# Object for handling xml
	handler = WikiXmlHandler()

	# Parsing object
	parser = xml.sax.make_parser()
	parser.setContentHandler(handler)

	# Iterate through compressed file
	for i, line in enumerate(bz2.BZ2File(data_path, 'r')):
		try:
			parser.feed(line)
		except StopIteration:
			break
			
		# Optional limit
		if limit is not None and len(handler._books) >= limit:
			return handler._books
	
	if save:
		partition_dir = 'Data/wiki/partitions/'
		# Create file name based on partition name
		p_str = data_path.split('-')[-1].split('.')[-2]
		out_dir = partition_dir + f'{p_str}.json'
		
		# Open the file
		with open(out_dir, 'w') as fout:
			# Write as json
			for book in handler._books:
				fout.write(json.dumps(book) + '\n')
		
		print(f'{len(os.listdir(partition_dir))} files processed.', end = '\r')

	# Memory management
	del handler
	del parser
	gc.collect()
	return None

partitions = ['Data/wiki/' + file for file in os.listdir('Data/wiki') if 'xml-p' in file]
len(partitions), partitions

print ("Going to start multiprocessing")

os.cpu_count()


start = timer()
start

if __name__ == "__main__":
	pool = Pool(processes = 3)

	results = pool.map(find_books, partitions)
	pool.close()
	pool.join()    

end = timer()
print(f'{end - start} seconds elapsed.')

