
import pandas as pd
import scripts.ETL as ETL ## Extract, Transform, Load - python script

import scripts.sql_queries_ml as ml ## machine learning script as well as plotting of relevant graphs
import datetime as dt

from flask import Flask, render_template, request

current_datetime = dt.date.today()
current_month = current_datetime.month
current_year = current_datetime.year
current_datetime = current_datetime.strftime('%A %B	%Y')


app = Flask(__name__)

def create_DB():

    print('couldnt find db, creating fresh')    
    # ETL Functionality 
    Starting_year = 17
    Ending_year = 22

    #initialize master_df to store all POS data
    master_df = pd.DataFrame()

    # Extract and Transform  - POS data  
    master_df = ETL.Load_master_df(master_df,Starting_year,Ending_year)

    # Initialize database name
    dbname = 'RestaurantDB'
    print("created db name")
    # Load transformed data into SQLite
    ETL.CreateDB(dbname, master_df) 
    return analysis()
    

def core():

    print('found db')
    Sales,session = ml.sql_connect()
    item_df,revenue_df, revenue_group_df, revenue_current_df, revenue_top_10, revenue_bot_10 = ml.sql_engine(Sales,session)
    print('tested for db before creating, loaded fine')
    #List of items that will appear in drop down menu
    items = item_df.item.unique()

    return (item_df,revenue_df, revenue_group_df, revenue_current_df, revenue_top_10, revenue_bot_10, items)

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/analysis')


def analysis():

    try: 
        test = request.args['variable']
        test = test.upper()

        if test == 'YES':

            try: 
                #Test for DB by executing core processes
                item_df,revenue_df, revenue_group_df, revenue_current_df, revenue_top_10, revenue_bot_10, items  = core()
                
                # Send links of files to index.html - hard coded limited links to visualisation for demonstration purposes.
                return render_template('analysis3.html',
                                       current_datetime = current_datetime,
                                       current_month = current_month,
                                       current_year = current_year, 
                                       item_df = item_df.to_json(orient='records'),
                                       revenue_df = revenue_df.to_json(orient='records'),
                                       revenue_current_df = revenue_current_df.to_json(orient='records'),
                                       revenue_group_df = revenue_group_df.to_json(orient='records'),
                                       revenue_top_10 = revenue_top_10.to_json(orient='records'),
                                       revenue_bot_10 = revenue_bot_10.to_json(orient='records'),
                                       items=items
                                        )
            except:    
                #If DB execution failed, create DB and run core processes
                create_DB()
                item_df,revenue_df, revenue_group_df, revenue_current_df, revenue_top_10, revenue_bot_10, items  = core()
                
                # Send links of files to index.html - hard coded limited links to visualisation for demonstration purposes.
                return render_template('analysis3.html',
                                       current_datetime = current_datetime,
                                       current_month = current_month,
                                       current_year = current_year, 
                                       item_df = item_df.to_json(orient='records'),
                                       revenue_df = revenue_df.to_json(orient='records'),
                                       revenue_current_df = revenue_current_df.to_json(orient='records'),
                                       revenue_group_df = revenue_group_df.to_json(orient='records'),
                                       revenue_top_10 = revenue_top_10.to_json(orient='records'),
                                       revenue_bot_10 = revenue_bot_10.to_json(orient='records'),
                                       items=items
                                        )
    except:

        return render_template('index.html')
    
if __name__ == '__main__':
    app.run(debug=True)