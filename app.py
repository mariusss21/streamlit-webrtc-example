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
import pymongo
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


# # Configurando o acesso ao mongodb
# myclient = pymongo.MongoClient("mongodb://192.168.81.128:27017/")
# mydb = myclient["mydatabase"]

# # upload de imagem para mongodb
# images = mydb.images


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

        status_bobina = st.selectbox('Status da bobina', ['Liberado', 'Não conforme']) # data
        descricao_bobina = st.text_input('Descrição:')
        conferente_bobina = st.text_input('Conferente:')
        quantidade_bobina = st.number_input('Quantidade:', format='%i', step=1, value=9000)
        lote_bobina = st.text_input('Lote SAP:')
        tipo_bobina = st.selectbox('Tipo', list(dict_tipo_bobinas.keys()))
        data_bobina = st.date_input('Data entrada:')

        submit_button = st.form_submit_button(label='Salvar bobina')

        if submit_button:
            tipo_de_etiqueta = ''
            
            if status_bobina == 'Não conforme':
                tipo_de_etiqueta = 'BLOQUEADO'

            if status_bobina == 'Liberado':
                tipo_de_etiqueta = 'LIBERADO'

            sap_bobina = dict_tipo_bobinas[tipo_bobina]
            
            texto_qrcode = ''.join(('tipo de etiqueta: ', tipo_de_etiqueta,
                ';Código SAP: ', sap_bobina,
                '; Descrição: ', descricao_bobina,
                '; Conferente:', conferente_bobina,
                '; Quantidade: ', str(quantidade_bobina),
                '; Lote: ', lote_bobina,
                '; Tipo:', tipo_bobina,
                '; Data entrada: ',str(data_bobina))                    
            )

            st.subheader('Informação do qrcode')
            st.write(texto_qrcode)

            imagem_bobina_qr = qrcode.make(texto_qrcode)
            image_bytearray = io.BytesIO()
            imagem_bobina_qr.save(image_bytearray, format='PNG')

            st.subheader('Inmagem do qrcode')
            st.image(image_bytearray.getvalue())
       

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


if __name__ == "__main__":

    c1,c2 = st.sidebar.columns([1,1])
    c1.image('logo2.png', width=150)

    st.sidebar.subheader('Bobinas')
    telas_bobinas = ['Entrada de bobinas', 'Inventário']
    tela_bobina = st.sidebar.radio('Menu bobinas', telas_bobinas)

    if tela_bobina == 'Entrada de bobinas':
        entrada_bobinas()

    if tela_bobina == 'Inventário':
        inventario_bobinas()
