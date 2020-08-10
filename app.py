from flask import Flask,render_template,request,jsonify
import sqlite3 as sql
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from collections import Counter
import plotly
import plotly.express as px
import json


#new words in sentiments
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

#homepage
@app.route('/')
def index():
    return render_template('index.html')
    
#add Nifty as a special page
# show the main link of all the stocks of the topstock    
@app.route('/topstock/', methods=['POST'])
def topstock():
    if request.method=='POST':
        text=request.form['search']
        if text=='NIFTY - S&P CNX NIFTY - INDEX':
            db,cur=connect('tsa')
            cur.execute('SELECT * FROM companies WHERE title==?',(text,))
            url_text=cur.fetchone()
            db.close()
            url=url_text[2]
            req= Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data= urlopen(req).read()
            # return render_template('test.html',data=data)
            soup=BeautifulSoup(data,'lxml')
            li=soup.find_all('div',{'class':'col-lg-4 col-md-4 col-sm-4'})[1:]
            val_list=[]
            final_dict={}
            h3=li[0].find('h3').text
            new_li=li[0].find('table').find_all('td')
            for val in new_li:
                val_list.append(val.text)
            val_dic={val_list[i]:val_list[i+1] for i in range(0,len(val_list),2)}
            final_dict[h3]= val_dic

            for div in li[1:4]:
                val_list=[]
                h3=div.find('h3').text
                new_li=div.find('table').find_all('td')
                for val in new_li:
                    val_dic={}
                    if len(val.attrs)!=0 :
                        if val.attrs['colspan']=='3':
                            pass
                        else:
                            
                            val_list.append(val.text.strip())
                    else:
                        val_list.append(val.text.strip())
                val_dic={val_list[i]:val_list[i+1:i+3] for i in range(0,len(val_list),3)}
                final_dict[h3]= val_dic

            val_list=[]
            h3=li[4].find('h3').text
            new_li=li[4].find('table').find_all('td')
            val_dic={}
            for val in new_li:
                if len(val.attrs)!=0 :
                    if val.attrs['colspan']=='2':
                        pass
                    else:
                        val_list.append(val.text.strip())
                else:
                    val_list.append(val.text.strip())
            val_dic={val_list[i]:val_list[i+1] for i in range(0,len(val_list),2)}
            final_dict[h3]= val_dic

            for div in li[4:8]:
                val_list=[]
                h3=div.find('h3').text
                new_li=div.find('table').find_all('td')
                for val in new_li:
                    val_dic={}
                    if len(val.attrs)!=0 :
                        if val.attrs['colspan']=='2':
                            pass
                        else:
                            val_list.append(val.text.strip())
                    else:
                        val_list.append(val.text.strip())
                val_dic={val_list[i]:val_list[i+1] for i in range(0,len(val_list),2)}
                final_dict[h3]= val_dic

            val_list=[]
            h3=li[8].find('h3').text
            new_li=li[8].find('table').find_all('td')
            for val in new_li:
                val_dic={}
                if len(val.attrs)!=0 :
                    if val.attrs['colspan']=='3':
                        pass
                    else:
                        val_list.append(val.text.strip())
                else:
                    val_list.append(val.text.strip())
            val_dic={val_list[i]:val_list[i+1:i+3] for i in range(0,len(val_list),3)}
            final_dict[h3]= val_dic

            li=soup.find('div',{'class':'col-lg-8 col-md-8 col-sm-8'})
            val_list=[]
            h3=li.find('h3').text.strip()
            for val in li.find_all('td'):
                if len(val.attrs)!=0 :
                    if val.attrs['colspan']=='1':
                        pass
                    else:
                        val_list.append(val.text.strip())
                else:
                    val_list.append(val.text.strip())
            final_dict[h3]= val_list
            final={}
            i=1
            for val in final_dict.items():
                final[i]=val
                i=i+1
   
            return render_template('nifty.html',data=final)
        else:
            db,cur=connect('tsa')
            cur.execute('SELECT * FROM companies WHERE title==?',(text,))
            url_text=cur.fetchone()
            db.close()
            url=url_text[2]
            req= Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data= urlopen(req).read()
            # return render_template('test.html',data=data)
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
            return render_template('topstock.html',data1=final_dict, data2=final_dict1,highlight=highlights[0:-1])

#show the fundamentals link
@app.route('/fund_ac/', methods=['POST'])
def screener():
    if request.method=='POST':
        text=request.form['search']
        db,cur=connect('tsa')
        cur.execute('SELECT * FROM companies WHERE title==?',(text,))
        url_text=cur.fetchone()
        db.close()
        url=url_text[3]
        req= Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data= urlopen(req).read()
        url_text=urlopen(req).read()
        soup=BeautifulSoup(url_text,'lxml')
        tab_li=soup.find_all('div',{'class':'table-responsive'})[0:4]
        fin_dic={}
        for val in tab_li[0:2]:
            dic={}
            td_li=[]
            h3=val.find('h3').text
            for th in val.find_all('th'):
                td_li.append(th.text.strip())  
            for td in val.find_all('td'):
                td_li.append(td.text.strip())
            for val1,val2 in zip(td_li[0::2],td_li[1::2]):
                dic[val1]=val2
            fin_dic[h3]=dic
        for val in tab_li[2:4]:
            td_li=[]
            h3=val.find('h3').text
            for th in val.find_all('th'):
                td_li.append(th.text.strip())  
            for td in val.find_all('td'):
                td_li.append(td.text.strip())
            dic1={td_li[k]:td_li[k+1:k+4] for k in range(0,len(td_li),4)}
            fin_dic[h3]=dic1
        data=[]
        for val in fin_dic.items():
            data.append(val)
        
    return render_template('screener.html',data=data)
    # url='https://www.screener.in/company/RELIANCE/consolidated/'
    # data=urlopen(url)
    # soup=BeautifulSoup(data,'lxml')
    # li=soup.find_all('ul',{'class':'row-full-width'})
    # orde=[]
    # for val in li:
    #     for var in val.find_all('li'):
    #         orde.append(var.text.split("\n"))
    # orde1=[]
    # for val in orde:
    #     orde1.append(list(filter(lambda item:item.strip(' '), val)))
    # orde=[]
    # for val in orde1:
    #     if (val[0].strip()=='Listed on') or (val[0].strip()=='Company Website'):
    #         pass
    #     elif len(val[1:])>1:
    #             new_val=val[1].strip() +" "+ val[2].strip()
    #             orde.append((val[0].strip(),new_val))
    #     else:
    #         orde.append((val[0].strip(),val[1].strip()))
    

    # url_peer='https://www.screener.in/api/company/6598251/peers/'
    # data=urlopen(url_peer)
    # soup=BeautifulSoup(data,'lxml')
    # peer=soup.find_all('table',{'class':'data-table text-nowrap striped'})
    # orde1=[]
    # for val in peer:
    #     for var in val.find_all('tr'):
    #         orde1.append(var.text)
    # peer_data=[]
    # for var in orde1:
    #     peer_data.append(var.split("\n"))
    # orde1=[]
    # for var in peer_data[1:3]:
    #     str_list=list(filter(lambda item:item.strip(), var))
    #     orde1.append(str_list[1:])
    # url='https://www.screener.in/company/RELIANCE/consolidated/'
    # data=urlopen(url)
    # soup=BeautifulSoup(data,'lxml')
    # li=soup.find_all('table',{'class':'three columns ranges-table'})
    # compound=[]
    # for val in li:
    #     data=val.find_all('td')
    #     for td in data[-2:]:
    #         compound.append(td.text.strip())
    # data=zip(compound[0::2],compound[1::2])

    # cash_flow=soup.find('section',{'id':'cash-flow'}).find('table')
    # th=cash_flow.find_all('th')
    # years=[]
    # for val in th[-3:]:
    #     years.append(val.text)
    # cash_flow_dic={}
    # cash_flow_dic[0]=years
    # td=cash_flow.find_all('tr')   
    # cost=[]
    # for val in td[1:]:
    #     cost.append(val)
    # for i in range(1,len(cost)+1):
    #     cash_flow_dic[i]=cost[i-1].text.split('\n')[-4:-1]

    # share_hold=soup.find('section',{'id':'shareholding'}).find('table')
    # th=share_hold.find_all('th')
    # years=[]
    # for val in th[4:]:
    #     years.append(val.text.strip())
    # share_dic={}
    # share_dic[0]=years
    # tr=share_hold.find_all('tr')
    # share=[]
    # for val in tr[1:]:
    #     share.append(val)
    # for i in range(1,len(share)+1):
    #     share_dic[i]=share[i-1].text.split('\n')[-10:-1]

    # return render_template('screener.html',data1=orde,peer=enumerate(orde1,start=1),compound=data,cash_data=cash_flow_dic,
    #                         share=share_dic)

#show the technicals links
@app.route('/trend_ac/', methods=['POST'])
def trend():
    if request.method=='POST':
        text=request.form['search']
        db,cur=connect('tsa')
        cur.execute('SELECT * FROM companies WHERE title==?',(text,))
        url_text=cur.fetchone()
        db.close()
        url=url_text[4]
        req= Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data= urlopen(req).read()
        url_text=urlopen(req).read()
        soup=BeautifulSoup(data,'lxml')
        tables=soup.find_all('div',{'id':'datagrid'})
        final_dic={}
        val_list=[]
        for th in tables[0].find_all('th'):
            val_list.append(th.text.strip())
        for val in tables[0].find_all('td'):
            val_list.append(val.text.strip())
        if len(val_list)==12:
            dic={val_list[i]:val_list[i+1:i+6] for i in range(0,len(val_list),6)}
        elif len(val_list)==14:
            dic={val_list[i]:val_list[i+1:i+7] for i in range(0,len(val_list),7)}
        elif len(val_list)==18:
            dic={val_list[i]:val_list[i+1:i+9] for i in range(0,len(val_list),9)}
        elif len(val_list)==16:
            dic={val_list[i]:val_list[i+1:i+8] for i in range(0,len(val_list),8)}

            
        final_dic['table']=dic


        val_list=[]
        h3=tables[1].find('h3').text.strip()
        for val in tables[1].find_all('td'):
            if len(val.attrs)!=0 :
                if val.attrs['colspan']=='1':
                    pass
                else:
                    val_list.append(val.text.strip())
            else:
                val_list.append(val.text.strip())
        final_dic[h3]=val_list
        signals=[]
        for val in tables[2:20]:
            val_list=[]
            dic={}
            h3=val.find('h3').text.strip()
            for th in val.find_all('th'):
                temp_td=val.find_all('td')
                if len(temp_td[2].text.strip())==0 and (th.text.strip()=='%K'):
                    pass
                else:
                    if th.find('a'):
                        pass
                    else:
                        if (th.text.strip()=='View In Chart') :
                            pass
                        else:
                            val_list.append(th.text.strip())
            for td in val.find_all('td'):
                if ('Volume Trend' in h3) and len(td.text.strip())==0:
                    val_list.append(" ")
                else:
                    if len(td.text)==1:
                        pass
                    else:
                        val_list.append(td.text.strip())
            if len(val_list)==16:
                dic={val_list[i]:val_list[i+1:i+4] for i in range(0,16,4)}
            if len(val_list)==20:
                dic={val_list[i]:val_list[i+1:i+5] for i in range(0,20,5)}
            if len(val_list)==24:
                dic={val_list[i]:val_list[i+1:i+6] for i in range(0,24,6)}
            if len(val_list)==32:
                dic={val_list[i]:val_list[i+1:i+4] for i in range(0,32,4)}
            
            sign=list(dic.values())
            for val in sign[1:]:
                signals.append(val[-1])

            final_dic[h3]=dic
        i=1
        data={}
        for val in final_dic.items():
            data[i]=val
            i=i+1
        
        sig_count=Counter(signals[0:-13])
        sig=dict(sig_count)
        df=pd.DataFrame(sig.items(),columns=['Signals','Value'])
        fig = px.bar(df, x="Signals", y="Value",color='Value',
             barmode='group',
             height=400,)  
        plot=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('comp_trend.html',data=data,plot=plot)

#connect to database
def connect(dbname):
    try:
        db=sql.connect(f"{dbname}.db")
        cur=db.cursor()
        return db,cur
    except Exception as e:
        print("Error" ,e)
        exit(2)

#fetch news from the cnbc and moneycontrol website
def fetchnews(dbname):
    if dbname=='cnbctv18':
        db,cur=connect('cnbctv18')
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
    
    elif dbname=='moneycontrol':
        db,cur=connect('moneycontrol')
        cur.execute('SELECT * FROM News ORDER BY id DESC LIMIT 1')
        lastrec=cur.fetchone()
        newslist=[]
        for var in range(1,3):
            url='https://www.moneycontrol.com/news/business/stocks/page-{0}'.format(var)
            data=urlopen(url)
            soup=BeautifulSoup(data,'lxml')
            li=soup.find_all('li',{'class':'clearfix'})
            for div in li:
                try:
                    link=div.find('a')['href']
                    title=div.find('a')['title']
                    desc=div.find('p').text
                    if title==lastrec[1]:
                        break
                    else:
                        score=vader.polarity_scores(title)['compound']
                        if score<0:
                            senti='negative'
                        elif score==0:
                            senti='netural'
                        else:
                            senti='positive'
                        newslist.append((title,desc,senti,link))
                except:
                    pass
            if title==lastrec[1]:
                break

        if len(newslist)!=0:        
                newslist=newslist[::-1]
                for val in newslist:
                    cur.execute("""INSERT INTO News(title,description,sentiment,link)
                        VALUES(?,?,?,?)""",(val[0].strip(),val[1].strip(),val[2],val[3]))
                    db.commit()
        db.close()


#Show the News
@app.route('/news/')
def news():
    fetchnews('cnbctv18')
    db,cur=connect('cnbctv18')
    cur.execute("""SELECT * FROM (
    SELECT * FROM News ORDER BY id DESC LIMIT 5
        )Var1 ORDER BY id ASC;""")
    news1=cur.fetchall()
    news1=news1[::-1]
    db.close()

    fetchnews('moneyconrol')
    db,cur=connect('moneycontrol')
    cur.execute("""SELECT * FROM (
    SELECT * FROM News ORDER BY id DESC LIMIT 5
        )Var1 ORDER BY id ASC;""")
    news2=cur.fetchall()
    news2=news2[::-1]
    db.close()
    return render_template('news.html',data1=enumerate(news1,start=1),data2=enumerate(news2,start=1))

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


@app.route('/money_news/')
def moneynews():
    db,cur=connect('moneycontrol')
    cur.execute("SELECT * FROM News")
    news=cur.fetchall()
    news=news[::-1]
    db.close()
    return render_template('money_control.html',data=enumerate(news,start=1))


@app.route('/part_money_news/', methods=['POST'])
def part_money_news():
    if request.method == 'POST':
        word=request.form['search']
        db,cur=connect('moneycontrol')
        cur.execute('Select * from News')
        news_list=cur.fetchall()
        word=word.lower()
        data=[]
        for news in news_list:
            if word in news[1].lower():
                data.append(news)
    db.close()
    return render_template("money_search.html",data=enumerate(data,start=1))


@app.route('/sgd/')
def receive_data():
    return render_template('tsa.html')

@app.route('/fundamentals/')
def fund_data():
    return render_template('fundamentals.html')

@app.route('/trends/')
def trend_data():
    return render_template('trend.html')

# show the corporate csv file
@app.route('/export/')
def export_lim():
    df=pd.read_csv('https://www1.nseindia.com/corporates/datafiles/BM_All_Forthcoming.csv').iloc[:10,:]
    data=list(df.values)
    return render_template('export_lim.html',data=data)

@app.route('/export_all/')
def export():
    df=pd.read_csv('https://www1.nseindia.com/corporates/datafiles/BM_All_Forthcoming.csv')
    data=list(df.values)
    return render_template('export_all.html',data=data)

@app.route('/export_part/', methods=['POST'])
def export_part():
     if request.method == 'POST':
        word=request.form['search']
        df=pd.read_csv('https://www1.nseindia.com/corporates/datafiles/BM_All_Forthcoming.csv')
        df=df[df['Company'].str.contains(word,case=False)]
        data=list(df.values)
        return render_template('part_export.html',data=data)


#show the graph in corporate page


if __name__ == "__main__":  
    app.run(debug = True) 