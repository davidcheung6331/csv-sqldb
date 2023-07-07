
import sqlite3
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain


#####################################
#            FUNCTIONS              #
#####################################
@st.cache_data()
def load_data(url):
    """
    load data from url
    """
    df = pd.read_csv(url)
    return df

def prepare_data(df):
    """
    lowercase columns
    """
    df.columns = [x.replace(' ', '_').lower() for x in df.columns]
    return df


#####################################
#        LOCALS & CONSTANTS         #
#####################################
table_name = 'statesdb'
uri = "file::memory:?cache=shared"


#####################################
#            HOME PAGE              #
#####################################
st.title('ChatGPT Pandas CSV Streamlit :house:')
st.subheader('Upload a file to query')

# read file
uploaded_file = st.file_uploader("Choose a csv file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)

    # api key
    openai_api_key = st.text_input(
        "API key", 
        placeholder='1234567890',
        type='password',
        disabled=False,
        help='Enter your OpenAI api key.'
    )

    # user query
    user_q = st.text_input(
        "User Query", 
        help="Enter a question based on the dataset")

    # commit data to sql
    data = prepare_data(df)
    conn = sqlite3.connect(uri)
    data.to_sql(table_name, conn, if_exists='replace', index=False)

    # create db engine
    eng = create_engine(
        url='sqlite:///file:memdb1?mode=memory&cache=shared', 
        poolclass=StaticPool, # single connection for requests
        creator=lambda: conn)
    db = SQLDatabase(engine=eng)

    # create open AI conn and db chain
    if openai_api_key:
      llm = OpenAI(
          openai_api_key=openai_api_key, 
          temperature=0, # creative scale
          max_tokens=300)
      db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)

    # run query and display result
    if openai_api_key and user_q:
        result = db_chain.run(user_q)
        st.write(result)