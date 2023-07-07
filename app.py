
import sqlite3
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from PIL import Image

# requirements
# streamlit
# langchain
# openai
# pandas
# SQLAlchemy

st.set_page_config(
    page_title="CSV to Database Query",
    page_icon="🗄",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """

st.markdown(hide_menu_style, unsafe_allow_html=True)
image = Image.open("customer-services.jpg")
st.image(image, caption='created by MJ')


# Cache the database and return dataframe by CSV file
@st.cache_data()
def load_data(url):
    df = pd.read_csv(url)
    return df

# Create the columns 
def prepare_data(df):
    df.columns = [x.replace(' ', '_').lower() for x in df.columns]
    return df


table_name = 'db1'
uri = "file::memory:?cache=shared"
st.title('🔍  :blue[Step 1: Query your CSV  by SqlDb]')

# display the content of CSV FILES
uploaded_file = st.file_uploader("Choose a CSV file to upload")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)

    st.title('🔍   :blue[Step 2: Enter your Query Text]')
    openai_api_key = st.text_input(
        ":key: OpenAI Key :", 
        placeholder='1234567890',
        type='password',
        disabled=False,
        help='Please enter your OpenAI api key.'
    )

    # user query
    user_q = st.text_input(
        "your Query Text : ", 
        help="Enter a question based on the CSV file")

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
        st.info(result)
