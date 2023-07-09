
from datetime import datetime, timedelta
import os

import numpy as np
import pandas as pd

import psycopg2
import requests
from transformers import pipeline

import plotly.graph_objects as go


class DB_interaction:
    
    def __init__(self):
        
        #print(os.environ['POSTGRES_USER'],os.environ['POSTGRES_PASSWORD'],os.environ['POSTGRES_HOST'],os.environ['POSTGRES_PORT'],os.environ['POSTGRES_DB'])
        
        self.connection = psycopg2.connect(
            user=os.environ['POSTGRES_USER'], #"postgres", 
            password=os.environ['POSTGRES_PASSWORD'], #"example",
            host=os.environ['POSTGRES_HOST'], #"localhost",
            port=os.environ['POSTGRES_PORT'], #"5432",
            database=os.environ['POSTGRES_DB'], #"sentimentapp"
        )
        self.cursor = None

        return
    
    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()
    
    
    def getCityIndexesDict(self):
        
        self.cursor = self.connection.cursor()
        
        self.cursor.execute("SELECT * FROM city_indexes;")
        selection = self.cursor.fetchall()
        #print(selection)
        
        city_indexes_dict = dict()
        for entry in selection:
            city_indexes_dict[ entry[1] ] = entry[2].split('|')
            
        self.cursor.close()
        
        return city_indexes_dict
    
    
    def isTodayInDB(self):
        
        today = datetime.now()
        
        self.cursor = self.connection.cursor()
        
        self.cursor.execute("SELECT MAX(date) FROM city_sentiment;")
        maxdate = self.cursor.fetchall()[0][0]
        
        self.cursor.close()
        
        if maxdate==today.date():
            return True
        
        return False
    
    
    def storeLatestSentiment(self, sentimentDict):

        if self.isTodayInDB():
            return "Date already present in the table city_sentiment"
        
        self.cursor = self.connection.cursor()
        
        today = datetime.now()
        
        for city, sentiment in sentimentDict.items():
            
            self.cursor.execute("\
                INSERT INTO city_sentiment (city, date, sentiment) \
                VALUES (\'"+city+"\', \
                        \'"+today.strftime("%Y-%m-%d")+"\', \
                        \'"+'|'.join(sentiment)+"' \
                );"
            )
        
        self.connection.commit()
        self.cursor.close()
        
        return "Today sentiment added to the table city_sentiment"
    
    
    def getLatestSentiment(self):
        
        self.cursor = self.connection.cursor()
        
        today = datetime.now()
        
        self.cursor.execute("\
            SELECT t1.city,t1.date,t2.lat,t2.lng,t1.sentiment \
            FROM (SELECT * \
            FROM city_sentiment \
            WHERE date=(SELECT MAX(date) FROM city_sentiment)) AS t1 \
            INNER JOIN city_table AS t2 ON t1.city=t2.city; \
        ")
        selection = self.cursor.fetchall()
        
        columns = [column[0] for column in self.cursor.description]
        
        df = pd.DataFrame(selection, columns=columns)
        
        self.cursor.close()
        
        return df
    
    def getCityLocations(self):
        pass
    
    

class MarketSentiment:
    
    def __init__(self):
        
        self._cityIndexesDict = list()
        self._sentimentDict = dict()
        
        self.newsapi_key = os.environ['NEWSAPI_KEY']
        
        self.sentiment_classifier = pipeline("sentiment-analysis", 
                                             model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
        
        return
    
    
    def addCityIndexes(self, CityIndexesDict):
        
        self._cityIndexesDict = CityIndexesDict
        
        for city, indexes in self._cityIndexesDict.items():
            
            self._sentimentDict[city] = self._computeWordSentiment(indexes)
        
        return
    
    
    def getSentiment(self):
        return self._sentimentDict
    
    
    def _computeWordSentiment(self, indexes):
        
        print(indexes)
        
        end_date = datetime.now()
        start_date = datetime.now()-timedelta(days=7)
        
        api_search_string = '\'\''+'\'\' OR \'\''.join(indexes)+'\'\''
        
        url = ('https://newsapi.org/v2/everything?q=' + api_search_string )+ \
               '&language=en&sortBy=relevancy&apiKey=' + self.newsapi_key + '&pageSize=100&page=1'+ \
               '&from='+start_date.strftime("%Y-%m-%d")+'&to='+end_date.strftime("%Y-%m-%d")
        print(url)

        all_articles = requests.get(url).json()
        
        s = list()
        
        for article in all_articles['articles']:
            
            try:
                sentiment_string = article['title']+'. '+article['description']+'. '+article['content']
            except:
                continue
            
            if all(index.lower() not in sentiment_string.lower() for index in indexes):
                continue
            sentiment = self.sentiment_classifier(sentiment_string)
            #print(sentiment_string,"\n",sentiment,"\n")
            
            s.append(sentiment[0]['label'])
            
        return s



class SentimentMap:
    
    def __init__(self, sentimentDf):
        
        self.map_sentiment = {'positive':1,'neutral':0,'negative':-1}
        
        self.sentimentDf = sentimentDf
        
        self.fig = None
        self._generate_plot()
        
        return
    
    def _generate_plot(self):
        
        df_market = self.sentimentDf.copy(deep=True)
        df_market = df_market[df_market.sentiment!='']
        #df_market = df_market.dropna(axis=0)
        
        sentiment_value = []
        sentiment_length = []
        
        for words in df_market.sentiment:
            s = words.split('|')
            
            if len(s)==0:
                continue
            
            value = np.mean([self.map_sentiment[x] for x in s])
            
            sentiment_value.append( value )
            sentiment_length.append( len(s) )
        
        df_market['sentiment_value'] = sentiment_value
        df_market['sentiment_length'] = sentiment_length
        df_market = df_market.dropna(axis=0)
        
        fig = go.Figure(data=go.Scattergeo(
            lon=df_market['lng'],
            lat=df_market['lat'],
            text=df_market['sentiment_value'].round(2),
            mode='markers',
            marker=dict(
                size = df_market['sentiment_length'],
                sizemode = 'area',
                color = df_market['sentiment_value'],
                cmin=-1, cmax = 1,
                colorscale=[(0, "red"),(0.5,"yellow"), (1, "green")],
                # colorbar=dict(
                #     title='Sentiment'
                # ),
                line=dict(
                    width=0.5,
                    color='rgb(40,40,40)'
                ),
                sizeref=2.0 / (20.0 ** 2),
                sizemin=1
            )
        ))
        fig.update_geos(
            projection_type="natural earth",
            #projection_type='equirectangular'
            #projection_type="orthographic",
            showcountries=False,
            showframe=True,
            showcoastlines=False,
        )
        fig.update_layout(title=df_market.date.unique()[0].strftime("%Y-%m-%d"),
                          margin={"r":10,"t":40,"l":10,"b":10})
        
        self.fig = fig
        
        return
    

