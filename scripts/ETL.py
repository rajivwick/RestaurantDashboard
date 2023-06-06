import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float 
from sqlalchemy.orm import Session

master_df = pd.DataFrame()

def Import_clean_dataset(df,month,year,master_df):
    
    # Drop first row - headers
    df = df.drop(labels=0)

    # Reset index
    df = df.reset_index()

    # Rename Columns
    df = df.rename(columns={'Unnamed: 1':'item','Unnamed: 3':'price','Unnamed: 4':'sold', 'Unnamed: 7':'tot_value'})
    
    # Keep only columns of interest
    df = df[['item','price','sold','tot_value']]
    
    # drop duplicates and NaN rows
    df = df.drop_duplicates()
    df = df.dropna()

    # Remove any leading or trailing spaces from string
    df['item'] = df['item'].str.strip()
    
    # Remove any commas from tot_value column entries
    df['tot_value'] = df['tot_value'].str.replace(r',', '')
    
   
    # Convert object type to numeric type
    df['tot_value'] = df['tot_value'].apply(pd.to_numeric, errors='coerce')
    df['sold'] = df['sold'].apply(pd.to_numeric, errors='coerce')
    df['price'] = df['price'].apply(pd.to_numeric, errors='coerce')
    
    # Create new columns to store month value
    df['month'] = month
    df['month'] = df['month'].astype(float)
    
    # Create new columns to store year value
    df['year'] = year
    df['year'] = df['year'].astype(float)
    
    # Creating new date field yyyy-mm-dd
    if month < 10:
        df['date'] = str(20)+str(year)+'-'+ str(0)+str(month)+'-'+'01'
    else:
        df['date'] = str(20)+str(year) + '-'+str(month)+'-'+'01'
        
    # Sort new Datafarme by total value
    df = df.sort_values(by='tot_value', ascending=False)

    # Add the generated df onto the master df
    master_df = master_df.append(df, ignore_index=True)
    
    return (master_df)

# Auto loading function created to seamlessly load the POS csv files without manual entry or hard coding.
def Load_master_df(master_df,Starting_year,Ending_year):

    # For range between starting year and ending year (+1)
    for year in range(Starting_year, Ending_year+1):
        main = 'Resources/POSdata/'
        
        # For range of 1-13 (12)
        for month in range(1,13):
            
            # If the month is greater than 10 following the naming convention below
            if month >=10:
                file = main + str(year) + "-" + str(month) + '.csv'
            else:
                file = main + str(year) + "-" + str(0) + str(month) + '.csv'
            print(f'The file: {file} has been loaded')
            df = pd.read_csv(file)

            # Store all POS data of all 72 files 
            master_df = Import_clean_dataset(df,month,year,master_df)

    # Set item column values to string type
    master_df['item'] = master_df['item'].astype(str)
    return (master_df)

def CreateDB(dbname,master_df): 

        Base = declarative_base()

        # Create sales table 
        class sales(Base):
            __tablename__ = 'sales'
            id = Column(Integer, primary_key=True)
            item = Column(String(255))
            price = Column(Integer)
            sold = Column(Integer)
            tot_value = Column(Float)
            month = Column(Integer)
            year = Column(Integer)
            date = Column(String(255))


        # Initialize SQLite
        sqlite = 'sqlite:///' + dbname + '.sqlite'
        engine = create_engine(sqlite)
        conn = engine.connect()
        Base.metadata.create_all(engine)
        session = Session(bind=engine)

        # Store and commit POS data into the sales table created
        for row in range(len(master_df)):
            
            sqldata = sales(item = master_df.loc[row,'item'],price = master_df.loc[row,'price'], sold = master_df.loc[row,'sold'],
            tot_value=master_df.loc[row,'tot_value'], month = master_df.loc[row,'month'], year = master_df.loc[row,'year'], date = master_df.loc[row,'date'] )
            session.add(sqldata)

        session.commit()
        conn.close()
        session.close()


