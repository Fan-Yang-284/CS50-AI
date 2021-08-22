import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = {}
    for file in os.listdir(directory):
        with open(os.path.join(directory,file),"r", encoding = "utf8") as f:
            contents = f.read()
            files[file] = contents
    
    return files

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    document = nltk.word_tokenize(document.lower())
    stopwords = set(nltk.corpus.stopwords.words('english'))

    words = []

    for word in document:
        if all(char in string.punctuation for char in word):
            continue
        elif word in stopwords:
            continue

        words.append(word)

    return words

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    counts = {}
    numDocuments = 0
    for file,contents in documents.items():
        numDocuments += 1
        filewords = set()
        for word in contents:
            if word not in filewords:
                filewords.add(word)
                if word not in counts:
                    counts[word] = 1
                else:
                    counts[word] += 1
    
    for word,value in counts.items():
        counts[word] = math.log(numDocuments/value)

    return counts

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidfs = {} # stores filenames : tf-idf value

    for file, contents in files.items():
        tfidfs[file] = 0 
        tf = {}
        for word in contents:
            if word in query:
                if word in tf:
                    tf[word] += 1
                else:
                    tf[word] = 1
        
        for word in tf:
            tfidfs[file] += tf[word]*idfs[word]

    allFiles = list(tfidfs.items())
    allFiles.sort(key = lambda x: x[1], reverse = True)

    return [file[0] for file in allFiles[:n]]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    scores = {}

    for sentence, words in sentences.items():
        sentenceScore = [0,0,sentence]
        for word in query:
            if word in words:
                sentenceScore[0] += idfs[word] # word idf
                sentenceScore[1] += 1/len(words) # query term density
        
        scores[sentence] = sentenceScore
    
    allSentences = list(scores.values())

    allSentences.sort(key = lambda x: (x[0],x[1]), reverse = True)
    res = []
    for sentence in allSentences:
        res.append(sentence[2])
    return res[:n]

if __name__ == "__main__":
    main()
