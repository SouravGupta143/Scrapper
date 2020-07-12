from flask import Flask,render_template,request
import sqlite3 as sql
from urllib.request import urlopen
from bs4 import BeautifulSoup
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

new_words = {
    'rise':50,
    'high':10,
    'jump':45,
    'drop':-100,
    'slip':-10,
    'fall':-100,
    'gain':20,
    'crush': 10,
    'beat': 5,
    'miss': -5,
    'trouble': -10,
    'fall': -100,
    'drop':-10,
    'buy':20,
    'sell':-10,
    'bullish':10,
    'bull':10,
    }
    # Instantiate the sentiment intensity analyzer with the existing lexicon
vader = SentimentIntensityAnalyzer()
    # Update the lexicon
vader.lexicon.update(new_words)

app=Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/topstock/')
def topstock():
    url='https://www.topstockresearch.com/INDIAN_STOCKS/REFINERIES/Reliance_Industries_Ltd.html'
    data=urlopen(url)
    soup=BeautifulSoup(data,'lxml')
    li=soup.find_all('table',{'class':'table table-bordered table-striped table-hover'})
    final=[]
    for val in li:
        final.append(val.find_all('td'))
    #for var in val.find_all('td')
    final1=[]
    arr=np.array(final)
    final=arr.take([0,4,8,9,10])
    final1=arr.take([2,3])
    final2=arr.take(12)
    final=final.tolist()
    final1=final1.tolist()
    i=1
    final_dict={}
    for val in final:
        lib=[]
        if len(val)%2==0:
            for value in val:
                lib.append(value.text.strip())
            dic={lib[k]:lib[k+1] for k in range(0,len(lib),2)}
            final_dict[i]=dic
            i=i+1
            
        else:
            lis=val[0:(len(val)-1)]
            for value in lis:
                lib.append(value.text.strip())
            dic={lib[k]:lib[k+1] for k in range(0,len(lib),2)}
            final_dict[i]=dic
            i=i+1

    i=1
    final_dict1={}
    for val in final1:
        lib=[]
        if len(val)%3==0:
            for value in val:
                lib.append(value.text.strip())
            dic1={lib[k]:lib[k+1:k+3] for k in range(0,len(lib),3)}
            final_dict1[i]=dic1
            i=i+1
            
        else:
            lis1=val[0:(len(val)-1)]
            for value in lis1:
                lib.append(value.text.strip())
            dic1={lib[k]:lib[k+1:k+3] for k in range(0,len(lib),3)}
            final_dict1[i]=dic1
            i=i+1
    highlights=[]
    for val in final2:
        highlights.append(val.text.strip())
    return render_template('topstock.html',data1=final_dict, data2=final_dict1,highlight=highlights)

@app.route('/screener/')
def screener():
    url='https://www.screener.in/company/RELIANCE/consolidated/'
    data=urlopen(url)
    soup=BeautifulSoup(data,'lxml')
    li=soup.find_all('ul',{'class':'row-full-width'})
    orde=[]
    for val in li:
        for var in val.find_all('li'):
            orde.append(var.text.split("\n"))
    orde1=[]
    for val in orde:
        orde1.append(list(filter(lambda item:item.strip(' '), val)))
    orde=[]
    for val in orde1:
        if (val[0].strip()=='Listed on') or (val[0].strip()=='Company Website'):
            pass
        elif len(val[1:])>1:
                new_val=val[1].strip() +" "+ val[2].strip()
                orde.append((val[0].strip(),new_val))
        else:
            orde.append((val[0].strip(),val[1].strip()))
    

    url_peer='https://www.screener.in/api/company/6598251/peers/'
    data=urlopen(url_peer)
    soup=BeautifulSoup(data,'lxml')
    peer=soup.find_all('table',{'class':'data-table text-nowrap striped'})
    orde1=[]
    for val in peer:
        for var in val.find_all('tr'):
            orde1.append(var.text)
    peer_data=[]
    for var in orde1:
        peer_data.append(var.split("\n"))
    orde1=[]
    for var in peer_data[1:3]:
        str_list=list(filter(lambda item:item.strip(), var))
        orde1.append(str_list[1:])
    url='https://www.screener.in/company/RELIANCE/consolidated/'
    data=urlopen(url)
    soup=BeautifulSoup(data,'lxml')
    li=soup.find_all('table',{'class':'three columns ranges-table'})
    compound=[]
    for val in li:
        data=val.find_all('td')
        for td in data[-2:]:
            compound.append(td.text.strip())
    data=zip(compound[0::2],compound[1::2])

    cash_flow=soup.find('section',{'id':'cash-flow'}).find('table')
    th=cash_flow.find_all('th')
    years=[]
    for val in th[-3:]:
        years.append(val.text)
    cash_flow_dic={}
    cash_flow_dic[0]=years
    td=cash_flow.find_all('tr')   
    cost=[]
    for val in td[1:]:
        cost.append(val)
    for i in range(1,len(cost)+1):
        cash_flow_dic[i]=cost[i-1].text.split('\n')[-4:-1]

    share_hold=soup.find('section',{'id':'shareholding'}).find('table')
    th=share_hold.find_all('th')
    years=[]
    for val in th[4:]:
        years.append(val.text.strip())
    share_dic={}
    share_dic[0]=years
    tr=share_hold.find_all('tr')
    share=[]
    for val in tr[1:]:
        share.append(val)
    for i in range(1,len(share)+1):
        share_dic[i]=share[i-1].text.split('\n')[-10:-1]

    return render_template('screener.html',data1=orde,peer=enumerate(orde1,start=1),compound=data,cash_data=cash_flow_dic,
                            share=share_dic)


def connect(dbname):
    try:
        db=sql.connect(f"{dbname}.db")
        cur=db.cursor()
        return db,cur
    except Exception as e:
        print("Error" ,e)
        exit(2)


def fetchnews(dbname):
    db,cur=connect(dbname)
    cur.execute('SELECT * FROM News ORDER BY id DESC LIMIT 1')
    lastrec=cur.fetchone()
    newslist=[]
    for var in range(1,5):
        url='https://www.cnbctv18.com/market/stocks/page-{0}/'.format(var)
        data=urlopen(url)
        soup=BeautifulSoup(data,'lxml')
        li=soup.find_all('div',{'class':'list_title'})
        for div in li: 
            link=div.find('a')['href']
            text=list(div.find('a').text.split('\n'))
            if text[0]==lastrec[1]:
                break
            score=vader.polarity_scores(text[0])['compound']
            if score<0:
                senti='negative'
            elif score==0:
                senti='netural'
            else:
                senti='positive'
            newslist.append((link,text,senti))
        if text[0]==lastrec[1]:
            break
    if len(newslist)!=0:        
        newslist=newslist[::-1]

        for val in newslist:
            cur.execute("""INSERT INTO News(title,description,link,sentiment)
                            VALUES(?,?,?,?)""",(val[1][0],val[1][1],val[0],val[2]))
            db.commit()
    db.close()
    return None



@app.route('/news/')
def news():
    fetchnews('cnbctv18')
    db,cur=connect('cnbctv18')
    cur.execute("""SELECT * FROM (
    SELECT * FROM News ORDER BY id DESC LIMIT 5
        )Var1 ORDER BY id ASC;""")
    news2=cur.fetchall()
    news2=news2[::-1]
    db.close()
    return render_template('news.html',data=enumerate(news2,start=1))

@app.route('/cnbctv/')
def cnbctv18news():
    db,cur=connect('cnbctv18')
    cur.execute("SELECT * FROM News")
    news=cur.fetchall()
    news=news[::-1]
    db.close()
    return render_template('cnbctv18.html',data=enumerate(news,start=1))

@app.route('/part_cnbc_news/', methods=['POST'])
def part_cnbc_news():
    if request.method == 'POST':
        word=request.form['search']
        db,cur=connect('cnbctv18')
        cur.execute('Select * from News')
        news_list=cur.fetchall()
        word=word.lower()
        data=[]
        for news in news_list:
            if word in news[1].lower():
                data.append(news)
    db.close()
    return render_template("cnbc_newser.html",data=enumerate(data,start=1))

if __name__ == "__main__":  
    app.run(debug = True) 