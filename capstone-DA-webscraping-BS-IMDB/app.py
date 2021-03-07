from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import numpy as np
from pylab import rcParams


#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

table = soup.find('div',attrs={'class':'lister-list'})
tr = table.find_all('div',attrs={'class':'lister-item mode-advanced'})
temp = [] #initiating a tuple

for i in range(1, len(tr)):
    #insert the scrapping process here
    row = table.find_all('div',attrs={'class':'lister-item-content'})[i]
    
    #get judul
    judul = row.find_all('a')[0].text
    judul = judul.strip() #for removing the excess whitespace
    
    #get rating
    rating = row.find_all('strong')[0].text
    rating = rating.strip()
    
    #get metascore
    metascore = row.find_all('span', attrs={'class':'metascore favorable'})
    if not metascore:
        metascore=0
    else :
        metascore=metascore[0].text
    
    #get vote
    votes = row.find_all('span',attrs={'name':'nv'})[0].text
    votes = votes.strip()
    
    temp.append((judul, rating,metascore, votes))  

temp = temp[::-1]

#change into dataframe
data = pd.DataFrame(temp, columns = ('judul','imdb_rating','metascore','votes'))
data['votes'] = data['votes'].str.replace(",","")
#insert data wrangling here
data['imdb_rating'] = data['imdb_rating'].astype('float')
data['metascore'] = data['metascore'].astype('int')
data['imdb_rating']=data['imdb_rating']*10
data['votes'] = data['votes'].astype('int')
data_tabel = data.copy()
data_tabel['imdb_rating']=data_tabel['imdb_rating']/10
data_tabel = data_tabel.sort_values('votes', ascending=False).reset_index(drop=True)
#end of data wranggling 

@app.route("/")
def index(): 
	
    card_data = data["votes"].mean()
	# generate plot
    top7_movie = data.sort_values('votes', ascending=False).head(7)
    rcParams['figure.figsize'] = 20, 7
    plt.plot( 'judul', 'imdb_rating', data=top7_movie, marker='o', markerfacecolor='blue', markersize=9, color='skyblue', linewidth=4)
    plt.plot( 'judul', 'metascore', data=top7_movie, marker='s', markersize=9,markerfacecolor='red', color='pink', linewidth=4)
    plt.title('perbandingan imdb score dan metascore')
    plt.legend()
	# Rendering plot
    # Do not change this
    figfile = BytesIO()
    plt.savefig(figfile, format='png', transparent=True)
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    plot_result = str(figdata_png)[2:-1]
    data_table = data_tabel.to_html(classes=["table table-bordered table-striped table-condensed"])

    # render to html
    return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
        table = data_table
		)


if __name__ == "__main__": 
    app.run(debug=True)
