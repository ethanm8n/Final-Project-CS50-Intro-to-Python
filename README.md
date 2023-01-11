# Library
#### Video Demo:  https://youtu.be/xaryq65pOfw
#### Description: A CS50 Tool for Managing a Dewey Decimal Library

## You want to sort some books?

I wanted to create a tool that sorts books into a library, based on Dewey Decimal.
But where do I get book data that I can manipulate with python?

I tried experimenting with a few api's when I came across [Open Library's Books API](https://openlibrary.org/books/). There were several reasons for choosing Open Library: Its queries return json objects, there is no sign in required, and it has a url to grab book data at random (https://openlibrary.org/random).
I could then collect random references to books in a easily modifiable format.

What I realised pretty early on implementing a function to sort books into each library class (Social sciences, Language, etc.), is that the process is relatively complex; the subjects of a book are not easily filtered down into 9 categories, unless I had the time to write an algorithim that covers every permutation of any subject ever written. My compromise was letting the user sort the books, one at a time.

### The program can be run in three modes:

## Sort Mode
1. Given a list of n books (picked at random from [Open Library's Books API](https://openlibrary.org/books/)) via the -s=n flag (where n is a positive int), sort them into a list of dicts
2. Save the result as inventory.json, where each key corrisponds to a category within the library, as per the Dewey Decimal Classification

## Find Mode
Given an author's name or title via the -r=inventory.json flag, return matching book(s)

## Recommend Mode
Given a book category and number of books via the -r=inventory.json flag, display a number of books that belong to that category

## Examples
```
    $ project.py -s=10 // create, sort a collection of 10 books
    $ project.py -f=file.json // search collection based on author or title
    $ project.py -r=file.json // recommend a random book of a chosen category
```
