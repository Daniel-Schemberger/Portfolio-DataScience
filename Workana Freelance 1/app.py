# Bibliotecas:

import streamlit as st
import pandas as pd
import gspread
import numpy as np
import json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io
import os
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ------------------------------------------------------------------

# Configuração da aplicação:

# Definições do Layout da aplicação, as configurações de theme estão na pasta .streamlit

st.set_page_config(layout='wide',
                   page_title='Epeixão App',
                   page_icon='epeixao.png'
                   )

# ------------------------------------------------------------------

# Definição de Funções:

# Duas funções foram definidas para a aplicação, uma para gerar uma mask com os filtros definidos
# e outra para gerar um PDF a partir de um dataframe

@st.cache_data
def multiselect_filter(dataframe, col, selecionados):

    """ Filtra o dataframe com base no filtro"""

    if 'Todos' in selecionados:
        return dataframe
    else:
        return  dataframe[dataframe[col].isin(selecionados)].reset_index(drop=True)

@st.cache_data    
def to_pdf(dataframe):
    
    """ Gera um PDF contendo o dataframe"""
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    
    data = [[""] + dataframe.columns.tolist()] + \
           [[index] + row.tolist() for index, row in dataframe.iterrows()]

    column_widths = [max(150, len(str(col)) * 20) for col in dataframe.columns]

    column_widths.insert(0, max(150, len(str(dataframe.index.name)) * 20))

    table = Table(data, colWidths=column_widths)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ])
    table.setStyle(style)

    elements.append(table)
    pdf.build(elements)

    buffer.seek(0)
    return buffer

# ------------------------------------------------------------------

# Aplicação: 


with st.sidebar:
    st.image('barco.jpg')
    st.title('App Propostas Rápidas')
    choice = st.radio('Etapas:', [
        'Upload dos dados', 'Filtros', 'Propostas'
    ])
    
file = None

# A aplicação é dividida em 3 planos, contidos no "choice" definido acima

# Primeiro plano:
if choice == 'Upload dos dados':

    st.title('Importação da Planilha')
    st.write('---')

    st.sidebar.write('Instrução:')
    st.sidebar.info('''
            Ao clicar no botão ao lado, toda sua planilha será
             carregada para aplicação. Após carregada, será mostrado
             um dataframe contendo todas as informações da planilha.
            
            Se toda planilha foi carregada com sucesso, basta passar 
            para a etapa "Filtros".''')
    

    if st.button('Clique para importar!'):

        # Importação dos dados da planilha, armazenamento em um dataframe "df". Armazenamento das imagens na pasta 
        # "Imagens"

        df = pd.read_csv('df.csv')
        st.write(df)

    else:
        st.write('Planilha ainda não foi carregada!')

else:
    pass

# Segundo plano:
if choice == 'Filtros':

    # Carregando os dados salvos
    df = pd.read_csv('df.csv')

    st.title('Defina os filtros')
    st.write('---')

    st.sidebar.write('Instrução:')
    st.sidebar.info('''
            Agora defina os filtros desejados selecionando as opções
            desejadas nos respectivos campos.
                    
            Caso não deseje filtrar por um campo específico, basta deixar
            "Todos" selecionado.
                    
            Após definir os filtros desejados, basta aplicar clicando no botão
            "Filtrar" e será gerado um dataframe contendo apenas os dados filtrados!
            ''')

    # Definição dos filtros:

    # Estado:

    lista_estado = df['UF'].unique().tolist()
    lista_estado.append('Todos')
    filtro_estado = st.multiselect('#### Estados:', lista_estado, ['Todos'])


    # Cidade:

    lista_cidade = df['CIDADE'].unique().tolist()
    lista_cidade.append('Todos')
    filtro_cidade = st.multiselect('#### Cidades:', lista_cidade, ['Todos'])


    # Barco:

    lista_barco = df['Nome do Barco'].unique().tolist()
    lista_barco.append('Todos')
    filtro_barco = st.multiselect('#### Barcos:', lista_barco, ['Todos'])


    # Dias:

    arr = df['Dias da Semana'].unique()
    lista_dias = list(set([dia.strip() for string in arr for dia in string.split(';')]))
    lista_dias.append('Todos')
    lista_dias.remove('')
    filtro_dias = st.multiselect('#### Dias da Semana:', lista_dias, ['Todos'])


    # Capacidade de Pessoas:

    lista_qtd_pessoas = df['N. Pessoas'].unique().tolist()
    lista_qtd_pessoas.append('Todos')
    filtro_qtd_pessoas = st.multiselect('#### Quantidade de Pessoas:', lista_qtd_pessoas, ['Todos'])   


    # Duração do Serviço (em horas):

    lista_tempo = df['Tempo Embarcado (H)'].unique().tolist()
    lista_tempo.append('Todos')
    filtro_tempo = st.multiselect('#### Duração:', lista_tempo, ['Todos'])


    # Preço:

    max_preco = int(max(df['Preço Barqueiro']))
    min_preco = int(min(df['Preço Barqueiro']))
    preco = st.slider(label='#### Preço:',
                      min_value=min_preco,
                      max_value=max_preco,
                      value=(min_preco, max_preco),
                      step=100)
    
    st.write('---')

    dic = {'UF': filtro_estado,
           'CIDADE': filtro_cidade,
           'Nome do Barco': filtro_barco,
           'Tempo Embarcado (H)': filtro_tempo,
           'N. Pessoas': filtro_qtd_pessoas}
    
    # Aplicação dos filtros
    st.write('## Aplicando os filtros')

    if st.button('Filtrar'):
        for col, filtro in dic.items():
            df = multiselect_filter(df, col, filtro)
        
        if 'Todos' in filtro_dias:
            pass
        else:
            for dia in filtro_dias:
                df = df[df['Dias da Semana'].str.contains(dia)]

        df = df[(df['Preço Barqueiro'] >= preco[0]) & (df['Preço Barqueiro'] <= preco[1])]

        st.write('Filtros aplicados com sucesso!')
        df.to_csv('df_filtrado.csv', index=False)
        st.write(df)

    else:
        st.write('Nenhum filtro foi aplicado!')


# Terceiro plano:
if choice == 'Propostas':

    st.title('Gerar Propostas')

    st.sidebar.write('Instrução:')
    st.sidebar.info('''
            Para gerar as propostas, basta indicar o ID do serviço
            e clicar em "Gerar Proposta".
                    
            Após gerar a proposta, é possível baixar um Excel com todas informações
            do serviço desejado.

            O segundo botão de Download baixa as informações do serviço no formato json.    
            ''')

    # Carregando os dados filtrados no plano 2
    df = pd.read_csv('df_filtrado.csv')
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'ID'})
    df.fillna('0', inplace=True)
    if df.shape[0] == 0:

        st.info('Nenhum serviço selecionado pelos filtros!')

    st.write('---')

    st.write('#### Dados Filtrados')

    df_fil = df[['ID', 'UF', 'CIDADE', 'Nome do Barco', 'Dias da Semana'
                 , 'Preço Barqueiro', 'Nome do Roteiro', 'Tempo Embarcado (H)',
                 'Cap. Barco', 'N. Pessoas']]
    

    if st.button('Ordenar por preço'):
        df_fil.sort_values(by='Preço Barqueiro', inplace=True)
        st.write(df_fil)
    else:
        st.write(df_fil)

    st.write('---')

    df_aux = df

    if st.button('Gerar Proposta'):
        st.write('# Propostas:')
        st.write('---')

        dic_dias = {'sábado; domingo; feriado': 'FINAL DE SEMANA E FERIÁDOS',
                    'seg; ter; qua; qui; sex': 'MEIO DE SEMANA',
                    'domingo; seg; ter; qua; qui; sex': 'MEIO DE SEMANA',
                    'sábado; feriado': 'SÁBADO E FERIADOS'}
        
        
        for barco in list(df_aux['Nome do Barco'].unique()):
            df_pivo = df_aux[df_aux['Nome do Barco'] == barco]
            df_pivo['Dias da Semana'] = df_pivo['Dias da Semana'].map(dic_dias)
            id_barco = df_pivo['ID Barco'].values[0]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f'### *{barco}* - Até {df_pivo["Cap. Barco"].values[0]} pessoas - {df_pivo["CIDADE"].values[0]} - {df_pivo["UF"].values[0]}<br> *VALORES DE ROTEIRO:*', unsafe_allow_html=True)

                for dias in list(df_pivo['Dias da Semana'].unique()):
                    df_pivo2 = df_pivo[df_pivo['Dias da Semana'] == dias]
                    st.markdown(f'### {df_pivo2["Dias da Semana"].values[0]}', unsafe_allow_html=True)
                    
                    for roteiro in list(df_pivo2['Nome do Roteiro'].unique()):
                        df_pivo3 = df_pivo2[df_pivo2['Nome do Roteiro'] == roteiro]
                        st.markdown(f'### Roteiro: *{df_pivo3["Nome do Roteiro"].values[0]}*', unsafe_allow_html=True)
                        
                        for qtd in list(df_pivo3['N. Pessoas'].unique()):
                            df_pivo4 = df_pivo3[df_pivo3['N. Pessoas'] == qtd]
                            st.markdown(f'#### R${df_pivo4["Preço Barqueiro"].values[0]}<br>{df_pivo4["N. Pessoas"].values[0]} Passageiros<br>Horário de Saída: {df_pivo4["Hora Saída "].values[0]}', unsafe_allow_html=True)

                st.markdown('---')
                st.markdown(f' #### Embarque: *{df_pivo4["Local de Embarque"].values[0]}* <br> Baixar proposta:', unsafe_allow_html=True)

                info = df_pivo2.transpose()
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    info.to_excel(writer,
                                sheet_name='Proposta')
                    workbook = writer.book
                    worksheet = writer.sheets['Proposta']
                    output.seek(0)

                st.download_button(label='Excel',
                                data=output,
                                file_name=f'proposta_{barco}.xlsx',
                                mime='xlsx')
                
                json_str = df_pivo2.to_json()

                st.download_button(label='JSON',
                                data=json_str,
                                file_name=f'proposta_{barco}.json',
                                mime='json')            
                
                st.markdown('---')

            if os.path.isfile(f'Imagens/{barco}.{id_barco}.jpeg'):
                col2.image(f'Imagens/{barco}.{id_barco}.jpeg', caption=barco, use_column_width=True)

    st.write('---')
    st.write('# Gerar JSON das Propostas')

    ids = st.text_input('Digite os ID cards das propostas selecionadas, separados por vírgulas:')
    st.info('Importar os dados sem digitar os id cards irá gerar os dados sem este campo!')

    if len(ids) != 0:
        if len(ids.split(',')) == df_aux.shape[0]:
            id_card = [int(ids.strip()) for ids in ids.split(',')]
    
            df_aux['id_card'] = id_card
            cols = ['id_card'] + [col for col in df_aux.columns if col != 'id_card']
            df_aux = df_aux[cols]
        else:
            st.info('Número de ID cards informada é diferente do número de propostas!')
    
    if st.button('Gerar JSON'):

        json_prop = df_aux.to_json()
        st.download_button(label='Baixar',
                            data=json_prop,
                            file_name=f'propostas.json',
                            mime='json')

    st.write('---')   
    st.write('# Gerar PDF das Propostas')

    st.write('### Selecione até 4 propostas para gerar um PDF')

    df_trans = df_aux.transpose()
    df_trans.index = df_aux.columns    

    if df.shape[0]>0:

        if(df.shape[0])<5:

            pdf = to_pdf(df_trans)

            st.download_button(label='Baixar PDF de todas propostas',
                       data=pdf,
                       file_name='pdf_propostas.pdf',
                       mime='application/pdf')
    
        else:
            st.write('##### -> **Muitas propostas selecionadas, não foi possível gerar o PDF**')
    else:
        st.write('Nenhuma proposta selecionada...')    