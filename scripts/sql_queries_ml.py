import pandas as pd
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

current_datetime = dt.date.today()
current_month = current_datetime.month

rice_items = [  'Pulao',
                'Yellow Rice Medium',
                'White Rice Medium',
                'Yellow Rice Large',
                'White Rice Large',
                'Jeera Rice Large'
      
                ]

naan_items = [  'Plain Naan',
                'Garlic Naan',
                'Chapattis',
                'Parathas',                        
                'Chili Naan',                
                'Cheese Nann'

            ]


entree_items = ['Curry Puffs',
                'Large Spring Rolls',
                'Large Samosas',
                'Samosas - Vege',
                'Mini Spring Rolls',
                'Curry Samosas',
                'Onion Bhajia',
                'chicken sticks'

                ]

misc_items = [
                'Pappodums x 4',
                'Raita',
                'Achar',
                'Mango Chutney',
                'Laccha',
                
                'Almond Kulfi',
                'Mango Kulfi',
                'Ice Cream',

                'Plain/Salted Lassi',
                'Sweet Mango Lassi',
                'Mango Nectar',
                'Falooda',
                'Can drinks',
                'Ginger Beer',
                'Cream Soda Glass Bt',
                'Boiled Channa',
                'Can drinks',
                'Glass Bottle 300ml',
                '1.25L drink',
                '2L DRNK',
                'Bottled Water',
                'Glass Bottle 300ml',
                'Bottled Water',
                'BYO',
                'BYO Per Head',
                'Sparking water',
                'Coconut Ice Cream',
                'Curd n Honey',
                'Coconut Water 500ml',
                'Cup Of Coffee',
                
                'Reuserble Bag',
                'Paper Carry Bag',
                'upgrade ONE SIZE',
                'upgrade TWO SIZES',
                'Cut Chilli',
                
                'Buchet of Ice',
                'Paper Carry Bag',
                'take away containers',
                'Reuserble Bag',

                'Cut Chilli',
                'Add Potato',
                'With spinach',
                'Extra Cashews',
                'Extra Garlic',
                'Extra Meat',
                
                'With Chicken',
                'With Beef'                
                ]


def sql_connect():
    print('sql engine started to load')
    # Set sqlite database name and input into the create_engine model from sqlalchemy 
    engine = create_engine("sqlite:///RestaurantDB.sqlite")

    # Use automap_base to auto map the Base classes found within the database
    Base = automap_base()
    Base.prepare(engine, reflect=True)

    # Create class assignments for required tables within the database
    Sales = Base.classes.sales


    # Create a session with SQLite
    session = Session(engine)
    print('sql engine started session')
    return(Sales,session)

def sql_total(Sales,session):

    # Initialize query calls from sales table     
        query = [Sales.item, Sales.sold, Sales.date, Sales.tot_value]

    # Query all data in the sales table relating to the query above    
        item_query = session.query(*query).all()

    # Store query results as a Dataframe and set column names
        item_df = pd.DataFrame(item_query, columns=['item', 'sold', 'date', 'total($)'])

    # Convert the date column to datetime type     
        item_df['date'] = pd.to_datetime(item_df['date'], format='%Y/%m/%d')

    # Sort the Dataframe by the date column      
        item_df = item_df.sort_values(by=['date'])

    # Clean Dataframe - drop duplicates and NaN values
        item_df = item_df.drop_duplicates()
        item_df = item_df.dropna()
            
        return item_df

def sql_item(Sales,session,item):
        print('entered sql_item module')
    # Initialize query calls from sales table 
        query = [Sales.item, Sales.sold, Sales.date, Sales.tot_value]
        
    # Query the SQLite database connected for all data relevant to the query layed out above relating to the type of meat in question.
        item_query = session.query(*query).\
        filter_by(item=item).all()

    # Store query results as a Dataframe and set column names    
        item_df = pd.DataFrame(item_query, columns=['item', 'sold', 'date', 'total($)'])
        print('first date formatting')
    # Convert the date column to datetime type     
        item_df['date'] = pd.to_datetime(item_df['date'], format='%Y/%m/%d')
        item_df = item_df.sort_values(by=['date'])
        #item_df = item_df.drop_duplicates()
        
        print(item_df.loc[1,'item'])
    # Sort the Dataframe by the date column    
        print('end of sql_item')   
        return item_df

def top_sales(Sales,session):
    # Query designed to deliver a descending array of item and their total sold counts
        query2 = [Sales.item, func.sum(Sales.sold)]

        total_sold = session.query(*query2).\
        group_by(Sales.item).all()

        total_sold_df = pd.DataFrame(total_sold, columns=['item', 'quantity']).\
        sort_values(by='quantity', ascending=False).reset_index(drop=True)  
        return total_sold_df 

def sql_engine(Sales,session):
        ignore_items = naan_items + rice_items + misc_items + entree_items   
        ignore_for_revenue = misc_items + entree_items
    # Store revenue data by using sql_total function
        revenue_df = sql_total(Sales,session)

    # Group by dates and count total revenue - apply some data cleaning and reset index
        revenue_group_df=revenue_df.groupby(revenue_df['date'].dt.strftime('%Y-%m')).sum().reset_index()

    #Revenue DF that stores the whole history of sold items - reduced to the data for the current year
        revenue_current_df = revenue_df[revenue_df['date'].dt.year == 2022]
        revenue_current_df = revenue_current_df[revenue_current_df['date'].dt.month == current_month]
    #Revenue DF grouped by Item and sorted by descending 
        revenue_current_df = revenue_current_df.groupby(revenue_df['item']).sum().reset_index().\
                                                sort_values(by='total($)',ascending=False)                                                

        revenue_current_df = revenue_current_df[~revenue_current_df['item'].isin(ignore_for_revenue)].\
                                                                            reset_index(drop=True)                                    

        revenue_current_top = revenue_current_df[~revenue_current_df['item'].isin(ignore_items)].\
                                                                            reset_index(drop=True)
        
        revenue_top_10 = revenue_current_top.truncate(after=9)
        
        revenue_bot_10 = revenue_current_top.sort_values(by='total($)',ascending=True).\
                                                                        reset_index(drop=True).\
                                                                        truncate(after=9)

    # Initialize item_df
        item_df = pd.DataFrame()
        print('creating item_df')
    # Created ignore_items as precursor for development with automated top and bottom 5-10 items analysis allowing for user to disregard any items of their choosing.    
        
    

        print('Before top Sales')
        total_sold_df = top_sales(Sales,session)
        print('after top sales')
        ####################################################################
        print('Before entering for loop')
        
        numberOfItems = 100
        
        for i in range(numberOfItems-1):
            # Used in conjunction with automated item analysis feature
            item = total_sold_df.loc[i,'item']
            
            if item not in ignore_items:
                print(i)
                item_df = item_df.append(sql_item(Sales,session,item), ignore_index=True)
                
                print(f'{item} added to df')
        print('outside of loop')
        
        item_df['Month'] = item_df['date'].dt.month
        
        print('about to covert dt')
        item_df['date'] = item_df['date'].apply(lambda x: x.strftime('%B %Y'))
        print ('about to return item info to app.py')




        return (item_df,revenue_df, revenue_group_df, revenue_current_df, revenue_top_10, revenue_bot_10)