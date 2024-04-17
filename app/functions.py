
import pandas as pd
import numpy as np

def search_topic(df: pd.DataFrame, user_input: str) -> pd.DataFrame:

    mention_indexes = np.where([ user_input in artigo for artigo in df['Conteúdo do Artigo'].values ])[0]
    return df.iloc[mention_indexes, :]
