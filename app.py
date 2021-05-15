from flask import Flask, render_template, url_for, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import os, json
from stemmer import Stemmer
stemmer = Stemmer('english')
invertedIndex = {}
positionalIndex = {}
queryWords = []

def loadIndices():
    global invertedIndex, positionalIndex
    with open('invertedIndex.json', 'r') as f:
        invertedIndex = json.load(f)

    with open('positionalIndex.json', 'r') as f:
        positionalIndex = json.load(f)

def queryProcessing(query):
    queryWords = []
    answer = []

    query = query.split()
    
    # Stemming the Query
    for word in query:
        if word == 'and' or word == 'or':
            queryWords.append(word)
        else:
            word = word.strip(',|!|.|"|;|:|-|_|#|+|@|)|(|?|~|`|[|]|{|}|=')
            queryWords.append(stemmer.stemWord(word))

    # Simple Query Processing (If the query only contains 1 word)
    if len(queryWords) == 1:
        try:
            answer = invertedIndex[queryWords[0]]
        except: 
            return "Word does not exist in the corpus"

    # Proximity Query
    elif queryWords[2][0] == '/':
        proximity = queryWords[2][1]
        intersection = [value for value in invertedIndex.get(queryWords[0]) if value in invertedIndex.get(queryWords[1])]
        intersection.sort(key=int)
        if intersection is not None:
            for doc in intersection:
                for j in positionalIndex[queryWords[0]][doc]:
                    for k in positionalIndex[queryWords[1]][doc]:
                        if ((k-j)) == int(proximity)+1:
                            answer.append(doc)

        else:
            return 'Both words do not appear in the same document and with the given proxmity.'
        return answer

    # Complex Query Processing (If the query is a boolean query)
    elif len(queryWords) > 1:

        if len(queryWords) == 3: # x and/or y
            if queryWords[1] == 'and':
                answer = [value for value in invertedIndex[queryWords[0]] if value in invertedIndex[queryWords[2]]]
            elif queryWords[1] == 'or':
                answer = list(set(invertedIndex[queryWords[0]]) | set(invertedIndex[queryWords[2]]))

        if len(queryWords) == 5: # x and/or y and/or z
            if queryWords[1] == 'and' and queryWords[3] == 'and': # x and y and z
                answer = [value for value in invertedIndex.get(queryWords[0]) if value in invertedIndex.get(queryWords[2])]
                if answer != None:
                    answer = [value for value in answer if value in invertedIndex.get(queryWords[4])]

            elif queryWords[1] == 'and' and queryWords[3] == 'or': # x and y or z
                answer = [value for value in invertedIndex.get(queryWords[0]) if value in invertedIndex.get(queryWords[2])]
                if answer != None:
                    answer = list(set(answer) | set(invertedIndex.get(queryWords[4])))
            
            elif queryWords[1] == 'or' and queryWords[3] == 'or': # x or y or z
                answer = list(set(invertedIndex[queryWords[0]]) | set(invertedIndex[queryWords[2]]))
                if answer != None:
                    answer = list(set(answer) | set(invertedIndex.get(queryWords[4])))



    if answer is None:
        return "Word does not exist in the corpus"
    else:
        answer.sort(key = int)
        return answer



    
class SearchForm(FlaskForm):
    query = StringField('Type boolean query here')
    submit = SubmitField('Search')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.debug = True

@app.route('/', methods=["GET", "POST"])
def searchPage():

    form = SearchForm()

    if form.submit.data:
        query = form.query.data.lower()
        
        # Processing Query
        answer = queryProcessing(query)


        return redirect(url_for('resultPage', answer=answer))
    return render_template('home.html', form=form)

@app.route('/result/<answer>', methods=['GET', 'POST'])
def resultPage(answer):
    return render_template('result.html', answer=answer)

if __name__ == '__main__':
    loadIndices()
    app.run()
