from stemmer import Stemmer
from os import listdir
import json, re

stopWords = ['"', '.', 'a', 'is', 'the', 'of', 'all', 'and', 'to', 'can', 'be', 'as', 'once', 'for', 'at', 'am', 'are', 'has', 'have', 'had', 'up', 'his', 'her', 'in', 'on', 'no', 'we', 'do']


stemmer = Stemmer('english')

invertedIndex = {}
positionalIndex = {}


files = listdir('ShortStories') # Get names of all files
location = 0

# Building the Inverted Index and the Positional Index
for file in files:
    with open(f'./ShortStories/{file}', 'r', encoding='utf8') as f:

        # Reading the whole file as a string and splitting each substring on spaces and special characters e.g: line break, encoded quotations etc.
        string = re.split(' |-|\n|\u00e3|\u2019|\u201c|\u201d|\u2014|\u2018|\u00a9|\u00af|\u00aa|\u00b4|\u00a7|\u00a8', f.read()) 
        
        location = 0

        for word in string:
            
            word = word.lower()
            # Stripping word and removing " ' : ; - _ # + @ ( ) / ? ~ ` [ ] { } =
            word = word.strip(',|!|.|"|;|:|-|_|#|+|@|)|(|/|?|~|`|[|]|{|}|=|\u00e3') 

            if word not in stopWords: # If word is not a stopword
                
                word = stemmer.stemWord(word) # Stemming

                # ========= Building Inverted Index =========
                # If the word already exists in the II, Append the word's document number in the II.
                # If the word does not exist in the II, add the word as a key and also add the document number.
                if word in invertedIndex:
                    if file.split('.')[0] not in invertedIndex[word]:
                        invertedIndex[word].append(file.split('.')[0])
                else: 
                    invertedIndex[word] = [file.split('.')[0]]

            # ========= Building Positional Index =========
            # If the word already exists in the PI, Append the word's document number and its position in the PI.
            # If the word does not exist in the OI, add the word as a key and also add the document number and the position of the word.
            if word in positionalIndex:
                if word not in stopWords:
                    if file.split('.')[0] in positionalIndex[word]:
                        positionalIndex[word][file.split('.')[0]].append(location)
                    else:
                        positionalIndex[word][file.split('.')[0]] = [location]
                
            else:
                if word not in stopWords:
                    positionalIndex[word] = {file.split('.')[0] : [location]}
            location += 1

invertedIndex.pop("")
positionalIndex.pop("")

# Writing to invertedIndex.json#
with open('./invertedIndex.json', 'w') as f:
    json.dump(invertedIndex, fp=f, sort_keys=True)
    
# Writing to positionalIndex.json
with open('./positionalIndex.json', 'w', encoding='utf8') as f:
    json.dump(positionalIndex, fp=f, sort_keys=True)