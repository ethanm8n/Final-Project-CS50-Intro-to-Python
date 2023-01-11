import requests
import re
import threading
import argparse
import sys
import json
import random

CATEGORIES = {
	'0': 'Computer science, information and general works',
	'1': 'Philosophy and psychology',
	'2': 'Religion',
	'3': 'Social sciences',
	'4': 'Language',
	'5': 'Science',
	'6': 'Technology',
	'7': 'Arts and recreation',
	'8': 'Literature'
}

def get_options() -> str:
	'''
	Give the user a multiple-choice question

	:returns:   A string of all questions
	:rtype:     { str }
	'''
	return ''.join([f'{key}) {CATEGORIES[key]}\n' for key in CATEGORIES])

def recommend(b: dict) -> list[dict]:
	'''
	Pick a random book of the user's preferred category

	:param      b:    A dict of all books
	:type       b:    dict

	:returns:   A list of book recommendations
	:rtype:     list[dict]
	'''
	options = get_options()
	result = []

	# Ask for book category
	while True:
		answer = input(f'What kind of book would you like?\n{options}').strip()

		# Repeat question if given no answer
		if answer != '':
			break

	# Grab matching category's books
	try:
		books_in_category = b[answer]
	except KeyError:
		sys.exit('Could not find category')

	# Exit if there are no books in that category
	if len(books_in_category) == 0:
		sys.exit('No books in that category')


	# Ask for how many books the user wants
	while True:
		if len(books_in_category) > 1:
			books_range = f'1-{len(books_in_category)}'
		else:
			books_range = '1'

		try:
			answer2 = int(input(f'How many books would you like? [{books_range}] ').strip())
		except ValueError:
			continue

		# User cannot ask for more books than there are in category, or for less than 0
		if answer2 > len(books_in_category):
			print('There are not that many books in this category')
			continue
		elif answer2 < 1:
			print('Please ask for 1 or more books')
			continue

		# Get random books in range
		result = random.sample(books_in_category, answer2)
		break

	return result

def search(b: dict) -> list[dict]:
	'''
	Grab book(s) that matches either the author or title inputed by the user, case insensitive

	:param      b:    A dict of all books
	:type       b:    dict

	:returns:   A list of search results
	:rtype:     list[dict]
	'''

	# Ask user for search query
	while True:
		answer = input('Enter an author\'s name or book title: ').lower().strip()

		# Repeat question if given no answer
		if answer != '':
			break

	results = []

	# For category in library
	for key in b:
		# For book in category
		for book in b[key]:
			try:
				# Grab author(s) id for GET request
				for author_id in book['authors']:
					try:
						author_key = author_id['key']
					except KeyError:
						print('Failed to find author key')

					# Make GET request for author name(s)
					try:
						author_response = requests.get(f'https://openlibrary.org{author_key}.json').json()
					except Exception:
						sys.exit('Failed to GET author')
					else:
						try:
							author = author_response['name']
						except KeyError:
							print('Failed to find author name')
						else:
							# Search more matching string in author's name
							if author.lower().find(answer.lower()) != -1:
								# Add match to results
								results.append(book)
			except KeyError:
				print('author key not found')

			# Grab title of book
			try:
				title = book['title']
			except KeyError:
				print('Failed to find title')
			else:
				# Search more matching string in title
				if title.lower().find(answer.lower()) != -1:
					# Add match to results
					results.append(book)

	return results

def classify(b: list[dict]) -> dict[str, list]:
	'''
	Ask user to put each book into a (overly simplified) Dewey Decimal Class:
	Class 0: Computer science, information and general works
	Class 1: Philosophy and psychology
	Class 2: Religion
	Class 3: Social sciences
	Class 4: Language
	Class 5: Science
	Class 6: Technology
	Class 7: Arts and recreation
	Class 8: Literature

	:param      b:    A list of unsorted books
	:type       b:    list[dict]

	:returns:   A dict of each category of books
	:rtype:     dict[list]
	'''

	classified_books = {
		'0': [],
		'1': [],
		'2': [],
		'3': [],
		'4': [],
		'5': [],
		'6': [],
		'7': [],
		'8': []
	}

	# Give the user a multiple-choice question
	options = get_options()

	for book in b:

		# Ask user to classify book
		while True:
			title = book['title']
			answer = input(f'Where should "{title}" go?\n{options}')

			try:
				# Check if class key exists
				CATEGORIES[answer]
			except KeyError:
				# Repeat question if answer did not match one of the classes
				print('Invalid answer\n')
				continue
			except KeyboardInterrupt:
				print('Goodbye\n')
			else:
				# If correct answer was given, stop asking and move on to next book
				classified_books[answer].append(book)
				break

	return classified_books

def create_json(b: dict[str, list], f='inventory.json') -> bool:
	'''
		Save categorized books into a .json file
		return True if file is saved successfuly, False otherwise

		:param      b:    dict of books
		:type       b:    dict[list]
		:param      f:    A boolean value, depending on successful write
		:type       f:    True or False
	'''

	# Create the json file
	with open(f, 'w') as file:

		# Populate file with library data
		try:
			json.dump(b, file, indent=1)
		except Exception:
			return False
			sys.exit(f'Error writing {f}')
		else:
			print(f'{f} saved')
			return True

def read_json(f='inventory.json') -> dict[str, list]:
	'''
		Read a .json file

		:param      b:    filename to read
		:type       b:    str
		:param      f:    A dict of books
		:type       f:    dict[list]
	'''

	with open(f, 'r') as file:
		# Read file data into a dict object
		try:
			data = json.load(file)
		except json.JSONDecodeError:
			sys.exit(f'Failed to read {f}')
		else:
			return data

class Books:
	def __init__(self, books=5):
		if books > 0:
			self.THREAD_COUNT = books
		else:
			raise TypeError('Expects 1 or more books, got a non-positive number')

		self._books = []
		self._threads_are_done = False

		# create a session object
		self._session = requests.Session()
		threads = []

		for i in range(self.THREAD_COUNT):
			# Put each request in a thread to spread the load
			thread = threading.Thread(target=self.get_random_book)
			thread.start()

		for thread in threads:
			# Wait for thread to complete
			thread.join()

		# Once threads are done, continue with program
		while True:
			if self._threads_are_done == True:
				break

	@property
	def books(self) -> list[dict]:
		return self._books


	def get_random_book(self) -> None:
		'''
		Grab a random book dict, append to self._books
		'''
		try:
			response = self._session.get('https://openlibrary.org/random')
		except Exception:
			print('response Error')

		# Trim the url, leaving the book's unique id at the end
		id_match = re.search(r'(https://openlibrary\.org/books/\w+)/', response.url)

		if id_match:
			# Format url with .json to match the API request
			url = id_match.group(1) + '.json'

		# Get random book data from the Open Library API
		print(f'GET {url}')
		try:
			api_response = self._session.get(url)
		except Exception:
			print('api_response Error')

		self._books.append(api_response.json())

		# Tell the main program that all threads are finsihed
		if len(self._books) == self.THREAD_COUNT:
			print('threads are done')
			self._threads_are_done = True

if __name__ == '__main__':
	# Setup argument parser
	parser = argparse.ArgumentParser(
		description='A CS50 Tool for Managing a Dewey Decimal Library',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog='library.py -s=10 # create, sort a collection of 10 books\nlibrary.py -f=file.json # search collection based on author or title\nlibrary.py -r=file.json # recommend a random book of a chosen category'
	)
	parser.add_argument('-s', '--sort', type=int, help='sort mode', nargs=1)
	parser.add_argument('-f', '--find', help='find mode', nargs=1)
	parser.add_argument('-r', '--recommend', help='recommend mode', nargs=1)
	args = parser.parse_args()

	if len(sys.argv) == 1:
		# Exit if no arguments were provided
		parser.print_help()
		sys.exit()

	elif args.sort:
		tomes = Books(args.sort[0]).books
		collection = classify(tomes)
		create_json(collection)

	elif args.find:
		# Grab library data from json file, if there is any
		data_to_search = read_json(args.find[0])
		if data_to_search == None:
			sys.exit('Could not read file; try running --sort')

		result = search(data_to_search)
		print(result)

	elif args.recommend:
		# Grab library data from json file, if there is any
		data_to_recommend = read_json(args.recommend[0])

		if data_to_recommend == None:
			sys.exit('Could not read file; try running --sort')

		recomendation = recommend(data_to_recommend)

		if recomendation == []:
			sys.exit('No recomendations were found')
		else:
				print(recomendation)

	else:
		sys.exit('Something went wrong with the arguments')
