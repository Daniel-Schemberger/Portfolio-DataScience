"""
    O código a seguir é a criação de uma aplicação que realiza análise
e segmentação de dados com RFV utilizando o Streamlit.
    A aplicação está online, com deploy feito pelo Render.
    
link da aplicação: https://app-rfv-wc1j.onrender.com

    Para utilizar a aplicação, basta carregar os dados disponibilizados
neste mesmo repositório com o nome "data.csv"
"""


import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

df = pd.read_csv('data.csv', parse_dates=['DiaCompra'])

dia_atual = df['DiaCompra'].max()

# Construção do Dataset:

df_rec = df.groupby(by='ID_cliente', as_index=False)['DiaCompra'].max()
df_rec.columns = ['ID_cliente', 'DiaUltimaCompra']

df_rec['recencia'] = df_rec['DiaUltimaCompra'].apply(
    lambda x: (dia_atual - x).days
)

df_rec.drop('DiaUltimaCompra', axis=1, inplace=True)

df_freq = df.groupby('ID_cliente')['CodigoCompra'].count().reset_index()
df_freq.columns = ['ID_cliente', 'frequencia']

df_val = df.groupby('ID_cliente')['ValorTotal'].sum().reset_index()
df_val.columns = ['ID_cliente', 'valor']

df_rfv = df_rec.merge(df_freq, on='ID_cliente')
df_rfv = df_rfv.merge(df_val, on ='ID_cliente')
df_rfv.set_index('ID_cliente', inplace=True)

# Segmentação:

quartis = df_rfv.quantile(q=[0.25, 0.5, 0.75])
quartis.to_dict()

# Funções:

def rec_class(x, r, q_dict):
    """Classifica como melhor o menor quartil
    x = valor da linha,
    r = recencia
    q_dict = dicionario do quartil"""

    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.5]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'
    
def freq_val_class(x, fv, q_dict):
    """Classifica como melhor o menor quartil
    x = valor da linha,
    fv = frequencia ou valor
    q_dict = dicionario do quartil"""

    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.5]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'  
    
df_rfv['r_quartil'] = df_rfv['recencia'].apply(rec_class, args=('recencia', quartis))
df_rfv['f_quartil'] = df_rfv['frequencia'].apply(freq_val_class, args=('frequencia', quartis))
df_rfv['v_quartil'] = df_rfv['valor'].apply(freq_val_class, args=('valor', quartis))

dict_acoes = {
    'AAA':
    'Enviar cupons de desconto, Pedir para indicar nosso produto pra algum amigo, Ao lançar um novo produto enviar amostras grátis pra esses.',
    'DDD':
    'Churn! clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
    'DAA':
    'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
    'CAA':
    'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar'
}

df_rfv['acoes_de_marketing/crm'] = df_rfv['score'].map(dict_acoes)

df_rfv.to_excel('./output/RFV.xlsx')
