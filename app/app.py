import streamlit as st
from functions import search_topic
import pandas as pd

c2 = pd.read_csv("../Data/cleaned/c2_cleaned.csv")

# Gather user topic
user_input = st.text_input("Please enter a topic to serach in the artigos of codigo civide: ")

st.write(user_input)

def search_topic2(df: pd.DataFrame, user_input: str)-> pd.DataFrame:

    mention_indexes = [ index for index, artigo in enumerate( list(df['Conteúdo do Artigo'].values) ) if user_input in artigo  ]
    return df.iloc[ mention_indexes, :]


if user_input:

	d = search_topic2(c2, user_input)
	
	st.dataframe(d)

		#st.write(user_input in content)


#st.write([ user_input in artigo for artigo in c2['Conteúdo do Artigo'].values ])

#filtered_dataframe = search_topic(c2, user_input)

#st.dataframe(filtered_dataframe)
