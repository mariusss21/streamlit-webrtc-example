######################################################################################################
                                 # importar bibliotecas
######################################################################################################

import streamlit as st
from streamlit import caching
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import numpy as np
#import json
#import smtplib
from datetime import  datetime, time
import pytz
#import base64
from io import StringIO
# import pymongo
from st_aggrid import AgGrid
# from pylogix import PLC
from PIL import Image
import io
import matplotlib.pyplot as plt
import cv2
from pyzbar.pyzbar import decode
import time
import qrcode
from PIL import Image
import json

from google.cloud import firestore
from google.oauth2 import service_account

key_dict = json.loads(st.secrets['textkey'])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project='logistica-invent')



######################################################################################################
                               #Funções
######################################################################################################

st.set_page_config(
     page_title="Inventário Logístico",
)

m = st.markdown("""
<style>
div.stButton > button:first-child{
    width: 100%;
    font-size: 18px;
}

label.css-qrbaxs{
    font-size: 18px;
}

p{
    font-size: 18px;
}

h1{
    text-align: center;
}

div.block-container{
    padding-top: 1rem;
}

div.streamlit-expanderHeader{
    width: 100%;
    font-size: 18px;
    background-color: rgb(240,242,246);
    color: black;
}
</style>""", unsafe_allow_html=True) #    font-weight: bold;


def read_barcodes(frame):

    barcodes = decode(frame)
    for barcode in barcodes:
        x, y , w, h = barcode.rect        #1
        barcode_info = barcode.data.decode('utf-8')             
        return barcode_info


def entrada_bobinas() -> None:
    st.subheader('Inserir bobina')

    dict_data = {}

    with st.form(key='myform'):
        texto_qrcode = ''

        dict_tipo_bobinas = {
        'BOBINA ALUMINIO LATA 16 OZ COIL 00098': 50761710,
        'BOBINA ALUMINIO LATA 12 OZ COIL 00098': 50679811,
        'BOBINA ALUMINIO LATA 12 OZ COIL 98 SCRAP': 40011008,
        'BOBINA ALUMINIO LACRE PRETO': 50552903,
        'BOBINA ALUMINIO LACRE AZUL': 50527602,
        'BOBINA ALUMINIO LATA 16 OZ': 50490762,
        'BOBINA ALUMINIO LATA 12 OZ': 50490761,
        'BOBINA ALUMINIO TAMPA PRATA REFRIG.': 50490760,
        'BOBINA ALUMINIO TAMPA DOURADO CERVEJA': 50490599,
        'BOBINA ALUMINIO LACRE PRATA': 50490598,
        'BOBINA ALUMINIO LATA 12 OZ SCRAP': 40010824,
        'BOBINA ALUMINIO TAMPA BRANCA': 50527252,
        'BOBINA ALUMINIO LACRE DOURADO': 50771048}

        dict_data['status'] = st.selectbox('Status da bobina', ['Liberado', 'Não conforme']) # data
        dict_data['descricao'] = st.text_input('Descrição:')
        dict_data['conferente'] = st.text_input('Conferente:')
        dict_data['quantidade'] = st.number_input('Quantidade:', format='%i', step=1, value=9000)
        dict_data['lote'] = st.text_input('Lote SAP:')
        dict_data['tipo'] = st.selectbox('Tipo', list(dict_tipo_bobinas.keys()))
        dict_data['data'] = st.date_input('Data entrada:')

        submit_button = st.form_submit_button(label='Salvar bobina')

        if submit_button:
            
            if dict_data['status'] == 'Não conforme':
                dict_data['tipo_de_etiqueta'] = 'BLOQUEADO'

            if dict_data['status'] == 'Liberado':
                dict_data['tipo_de_etiqueta'] = 'LIBERADO'

            dict_data['sap'] = dict_tipo_bobinas[dict_data['tipo']]
            
            # dict_data['texto_qrcode'] = ''.join(('tipo de etiqueta: ', dict_data['tipo_de_etiqueta'],
            #     '; Código SAP: ', dict_data['sap_bobina'],
            #     '; Descrição: ', dict_data['descricao_bobina'],
            #     '; Conferente:', dict_data['conferente_bobina'],
            #     '; Quantidade: ', str(dict_data['quantidade_bobina']),
            #     '; Lote: ', dict_data['lote_bobina'],
            #     '; Tipo:', dict_data['tipo_bobina'],
            #     '; Data entrada: ',str(dict_data['data_bobina']))                    
            # )

            doc_ref = db.collection('bobinas').document('bobinas')
            doc = doc_ref.get()

            if doc.exists:
                dicionario = doc.to_dict()
                csv = dicionario['dataframe']

                csv_string = StringIO(csv)
                df_bobinas = pd.read_csv(csv_string, sep=',')

                df_bobinas = df_bobinas.append(dict_data, ignore_index=True)

                dados = {}
                dados['dataframe'] = df_bobinas.to_csv(index=False)

                doc_ref.set(dados)
            else:
                df_bobinas = pd.DataFrame(dict_data, index=[0])
                dados = {}
                dados['dataframe'] = df_bobinas.to_csv(index=False)

                doc_ref.set(dados)

            # st.subheader('Informação do qrcode')
            # st.write(texto_qrcode)

            # imagem_bobina_qr = qrcode.make(texto_qrcode)
            # image_bytearray = io.BytesIO()
            # imagem_bobina_qr.save(image_bytearray, format='PNG')

            # st.subheader('Inmagem do qrcode')
            # st.image(image_bytearray.getvalue())
       

def inventario_bobinas() -> None:
    st.subheader('Inventário de bobinas')
    nome_inventario = st.text_input('Nome do inventário')
    data_inventario = st.date_input('Data do inventário')

    video_frame = st.file_uploader('Tire uma foto do qrcode da bobina')

    if video_frame is not None:
        file_bytes = io.BytesIO(video_frame.getvalue())
        image = cv2.imdecode(np.frombuffer(file_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        valor = read_barcodes(blur)
        st.write(valor)

        if valor is not None:
            st.button('Inventariar bobina')


def download_etiqueta(qrcode: str, dados_bobina: pd.DataFrame) -> None:
    st.write(qrcode)
    st.write(dados_bobina)


def etiquetas_bobinas() -> None:
    st.subheader('Etiquetas de bobinas')

    doc_ref = db.collection('bobinas').document('bobinas')
    doc = doc_ref.get()

    if doc.exists:
        dicionario = doc.to_dict()
        csv = dicionario['dataframe']

        csv_string = StringIO(csv)
        df_bobinas = pd.read_csv(csv_string, sep=',')

        data_etiqueta = st.date_input('Data da etiqueta')
        status_etiqueta = st.selectbox('Tipo de etiqueta', ['Liberado', 'Não conforme'])

        df_bobinas['data'] = pd.to_datetime(df_bobinas['data']).dt.date
        df_etiqueta_dia = df_bobinas.loc[(df_bobinas['data'] == data_etiqueta) & (df_bobinas['status'] == status_etiqueta)]

        if df_etiqueta_dia.empty:
            st.warning('Não há bobinas para a data e tipo de etiqueta informado')
        else:
            lista_etiquetas = list(df_etiqueta_dia.index)

            df_etiqueta_dia['data'] = pd.to_datetime(df_etiqueta_dia['data']).dt.strftime('%d/%m/%Y')

            for bobina in lista_etiquetas:
                texto_expander = ''.join(('Lote: ', str(df_etiqueta_dia.loc[bobina]['lote']), ' Quantidade: ', str(df_etiqueta_dia.loc[bobina]['quantidade'])))
                with st.expander(texto_expander):
                    texto_qrcode = ''
                    for colunas in df_bobinas.columns:
                        texto_qrcode = ''.join((texto_qrcode, str(df_bobinas.loc[bobina, colunas]), ','))
                        st.write(f'**{colunas}:** {df_bobinas.loc[bobina, colunas]}')

                    botao_download_etiqueta = st.button('Download etiqueta')
                    if botao_download_etiqueta:
                        download_etiqueta(texto_qrcode, df_bobinas.loc[bobina,:])

    
def login_session_state() -> None:
    senha = st.secrets['pass']
    senha_input = st.text_input('Senha:', type='password')

    botao_logar = st.button('Logar')

    if botao_logar:
        if senha_input == senha:
            st.session_state['logado'] = True
            st.experimental_rerun()
        else:
            st.error('Senha incorreta')


if __name__ == "__main__":
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False

    if st.session_state['logado'] == False:
        login_session_state()

    c1,c2 = st.sidebar.columns([1,1])
    c1.image('logo2.png', width=150)

    st.sidebar.subheader('Bobinas')
    telas_bobinas = ['Entrada de bobinas', 'Etiquetas', 'Inventário']
    tela_bobina = st.sidebar.radio('Menu bobinas', telas_bobinas)

    if st.session_state['logado'] == True:
        botao_sair = st.sidebar.button('Sair')

        if botao_sair:
            st.session_state['logado'] = False
            st.experimental_rerun()

        if tela_bobina == 'Entrada de bobinas':
            entrada_bobinas()

        if tela_bobina == 'Inventário':
            inventario_bobinas()

        if tela_bobina == 'Etiquetas':
            etiquetas_bobinas()
