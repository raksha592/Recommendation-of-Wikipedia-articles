# Recommendation-of-Wikipedia-articles
Wikipedia being one of the largest encyclopedia repositories in the world not only makes it a rich source of information, but also makes it a rich source of data for various Data Science Projects. Today, our focus is to build a Book Recommendation system for Wikipedia. We will be doing this using **Neural network embeddings**.
This tutorial will walk you through 3 basic steps involved in creating a recommender system for Wikipedia:
1.	Data Wrangling
2.	Data Preprocessing
3.	Neural Network embedding to recommend wiki articles

## Data Wrangling:
We can access the wiki dumps for all articles on this link: [Wikipedia dumps](https://meta.wikimedia.org/wiki/Data_dumps) 
The link provides access to various wiki dumps right from the complete articles to just the article titles or abstracts. For the purpose of this project, we are interested the complete list of articles which have been partitioned into various folders. Let us look at how we would be extracting these dumps.

One might think that this problem could be solved by parsing the Wikipedia web pages and extracting information individually from each of those pages. But this clearly isn’t an option which is feasible as our system would run into rate limits. Also, Wikipedia has millions of articles and to scrape each page individually is just taxing!

Let us look at how we would programmatically parse through and extract the English language Wikipedia articles in an efficient way.
We will first parse through [https://dumps.wikimedia.org/enwiki/](https://dumps.wikimedia.org/enwiki/) . We do this using BeautifulSoup to parse through HTML pages. We will be using dumps from September 2018 for our analysis.
The most recent revision of every single article is available in a single compressed file as ‘pages-articles.xml.bz2’. However, we'll download the articles in smaller chunks so that we can then process them in parallel (which we'll see later). The total file size of these articles is 15GB when compressed. They are divided into 55 partitions and we will be downloading all of them using keras utilities. **The default download directory of keras is /Keras/Datasets. To change this, I have manually added the file path on line number 48. You may do the same if you wish to change the path.**

Once we have downloaded the compressed files, we need to parse through them to extract the information we need. In our case, we need to extract all the articles which are related to 'Books'. To do this, we are using the following libraries:
1. bz2 library: To parse through Bz2 files
2. SAX library: To parse through XML files 
3. mwparserfromhell: This library is specifically for wikipedia dumps, it helps us parse through the articles and find the information we need using in-built functions.

The contentHandler class in the SAX parser looks for content between a start tag and an end tag. We will be editting this contenthandler class to extract only the information we need. To do that, we are going to create a new function called "process_article" to extract title, properties, wikilinks, exlinks, timestamp, text_length. We will be editting the contenthandler class to provide us with just the information we need.

Next, we will save all the books we found into JSON files. We will process each of these XML files in parallel using pooling to save time. This process took about 15 hours to process all the 55 partitions. The information is saved in 55 different JSON files.

We will be using these JSON files to build a Neural network Embedding to Recommend Wikipedia articles as shown in this [Notebook](https://github.com/raksha592/Recommendation-of-Wikipedia-articles/blob/master/Neural%20Network%20Embedding.ipynb)
