import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns

from pytrends.request import TrendReq



def pytrends_data(kw_list, kwIOT_df):
    
    pytrend_df = pd.DataFrame()
    pytrend = TrendReq(hl='en-US', tz=-480)  # initialise TrendReq
   
    location = 'AU-WA'
    cat = '0'
    timeframe1 = 'now 7-d'
    pytrend.build_payload(kw_list, cat=cat, timeframe=timeframe1, geo=location, gprop='')

    trends = pytrend.related_queries() # Build pytrends payload and query

    kwTop = trends[kw_list[0]]["top"] # kwTop to store the results of top trends similar to the keyword
    kw_list_group = []
    for row in range(len(kwTop)):
        search_term = kwTop.loc[row,'query']
        accurate_word = "indian"
        if accurate_word in search_term:
            kw_list_group.append(search_term)
    
    pytrend.build_payload(kw_list_group, cat=0, timeframe='2017-01-01 2022-12-1', geo='AU-WA', gprop='')
    pytrend_df = pytrend.interest_over_time()

    kwIOT_df = pd.DataFrame()

    for i in range(len(kw_list_group)):
        word = kw_list_group[i]
        kwIOT = pytrend_df[kw_list_group[i]] # kwTop to store the results of top trends similar to the keyword.
        kwIOTi = kwIOT.to_frame()
        kwIOT_df = kwIOT_df.append(kwIOTi[word])

    kwIOT_df=kwIOT_df.T
    kwIOT_df['total count'] = kwIOT_df[kw_list_group].sum(axis=1)

    return (kwIOT_df)

def Plot_trends(kwIOT_df):
    
    nowDate = dt.datetime.now().date()

    x = kwIOT_df.index
    y = kwIOT_df['total count']
    plt.scatter(x,y)
    
    plt.title("Related Searches in Western Australia",fontsize=20)
    plt.legend(['quantity'], loc='best')
    plt.xlabel('year', fontsize=15)
    plt.ylabel('total searches', fontsize=15)
    plt.savefig(f'static/images/SearchTrend-{nowDate}.png',bbox_inches='tight',pad_inches=0.2, transparent=True)

def sea_scatter(kwIOT_df, kw_index):

    nowDate = dt.datetime.now().date()

    g=sns.scatterplot(
                    data=kwIOT_df,
                    x=kw_index, 
                    y='total count',
                    size='total count', 
                    legend=False, 
                    palette="muted")
    g.set_ylabel('Total Search Count',fontsize=16)
    g.set_xlabel('Date',fontsize=16)

    plt.title('Related Searches in Western Australia',fontsize=20)

    plt.savefig(f'static/images/SearchTrend-{nowDate}.png',bbox_inches='tight',pad_inches=0.2, transparent=True)