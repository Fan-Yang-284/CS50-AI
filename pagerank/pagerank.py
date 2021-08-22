import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    
    probabilities = {}
    
    #probabilities for choosing a random page
    for k in corpus.keys():
        if len(corpus[page]) == 0:
            probabilities[k] = 1/len(corpus)
        else:
            probabilities[k] = (1/len(corpus))*(1-damping_factor)
    
    #if page has no external links
    if len(corpus[page]) == 0:
        return probabilities

    #probabilities for choosing a random link
    for link in corpus[page]:
        if link in probabilities:
            probabilities[link]+=(1/len(corpus[page]))*(damping_factor)
    
    return probabilities
    
    



def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    counts = {}
    for i in range(n):
        if i == 0:
            page = random.choice(list(corpus.keys())) 
        else:
            page = random.choices(list(corpus.keys()), list(transition_model(corpus,prev,damping_factor).values()))
            page = page[0] # random.choices returns a list item with length 1

        prev = page # keep track of previous pages to be used to generate transition model

        #print(page)
        if page in counts:
            counts[page]+=1
        else:
            counts[page]=1
    
    #get final probabilities
    for k,v in counts.items():
        counts[k]/=n
    
    return counts


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    rank = {}
    pages = len(corpus)
    for page in corpus:
        rank[page] = 1/pages
    
    while True:
        changes = 0 # will stop when there have been no significant changes
        for page in rank:
            currValue = rank[page] # to be compared with new value
            rank[page] = (1-damping_factor)/pages 
            for secondaryPage in rank:
                if secondaryPage == page:
                    continue
                links = len(corpus[secondaryPage])
                if links > 0 and page not in corpus[secondaryPage]: 
                    continue # if this page has links but none to the original page

                elif links == 0:
                    links = pages # assume links to every page

                rank[page] += damping_factor*(rank[secondaryPage]/links)
                
            if abs(rank[page]-currValue)>0.001:
                changes+=1

        #print(rank)
        if changes == 0:
            break
    
    return rank

if __name__ == "__main__":
    main()
