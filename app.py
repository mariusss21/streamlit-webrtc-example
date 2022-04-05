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
import base64
from io import StringIO, BytesIO
# import pymongo
# from st_aggrid import AgGrid
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
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as Image_openpyxl
from openpyxl.styles import Font, Color

#from webcam import webcam
import asyncio
import logging
import queue
import threading
import urllib.request
from pathlib import Path
from typing import List, NamedTuple

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

import av
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pydub
import streamlit as st
from aiortc.contrib.media import MediaPlayer

from streamlit_webrtc import (
    AudioProcessorBase,
    RTCConfiguration,
    VideoProcessorBase,
    WebRtcMode,
    webrtc_streamer,
)

# RTC_CONFIGURATION = RTCConfiguration(
#     {
#       "RTCIceServer": [{
#         "urls": ["turn:turn.xxx.dev:5349"],
#         "username": "user",
#         "credential": "password",
#       }]
#     }
# )

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


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

    with st.form(key='myform', clear_on_submit=True):
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

            if (dict_data['conferente'] == '') or (dict_data['lote'] == ''):
                st.error('Preencha todos os campos')
            else:
                    
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
                    df_bobinas.drop_duplicates(inplace=True)

                    dados = {}
                    dados['dataframe'] = df_bobinas.to_csv(index=False)

                    doc_ref.set(dados)
                else:
                    df_bobinas = pd.DataFrame(dict_data, index=[0])
                    df_bobinas.drop_duplicates(inplace=True)

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
        

@st.cache(allow_output_mutation=True)
def get_cap():
    cap = cv2.VideoCapture(0)
    return cap


def VideoProcessor():
    class video_processor(VideoProcessorBase):

        def __init__(self):
            self.result_queue = queue.Queue()
        
        def recv(self, frame):
            img = frame.to_ndarray(format='bgr24')
            # file_bytes = io.BytesIO(img.getvalue())
            # image = cv2.imdecode(np.frombuffer(file_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
            # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #img = cv2.medianBlur(img, 5)
            #valor = read_barcodes(blur) 
            decoder = cv2.QRCodeDetector()
            data, points, _ = decoder.detectAndDecode(img)

            if data != '' and data is not None:
                self.result_queue.put(data)
            
            if points is not None:
                # print('Decoded data: ' + data)
            
                points = points[0]
                for i in range(len(points)):
                    pt1 = [int(val) for val in points[i]]
                    pt2 = [int(val) for val in points[(i + 1) % 4]]
                    cv2.line(img, pt1, pt2, color=(255, 0, 0), thickness=3)
                    cv2.putText(img=img, text=data, org=(10, 10), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(255, 0, 0),thickness=1)

            return av.VideoFrame.from_ndarray(img, format='bgr24')

    webrtc_ctx = webrtc_streamer(key='exampe',
        video_processor_factory=video_processor,
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},)

    if st.checkbox("Show the detected labels", value=True):
        if webrtc_ctx.state.playing:
            labels_placeholder = st.empty()
            # NOTE: The video transformation with object detection and
            # this loop displaying the result labels are running
            # in different threads asynchronously.
            # Then the rendered video frames and the labels displayed here
            # are not strictly synchronized.
            while True:
                if webrtc_ctx.video_processor:
                    try:
                        result = webrtc_ctx.video_processor.result_queue.get(
                            timeout=1.0
                        )
                    except queue.Empty:
                        result = None
                    labels_placeholder.write(result)
                else:
                    break


def inserir_invetario() -> None:
    st.subheader('Inventário de bobinas')

    VideoProcessor()
    nome_inventario = st.text_input('Nome do inventário')
    data_inventario = st.date_input('Data do inventário')

    st.button('teste')
    # video_frame = st.file_uploader('Tire uma foto do qrcode da bobina')

    # cap = get_cap()
    # frame_st = st.empty()

    # while True:
    #     ret, video_frame = cap.read()
    #     video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
    #     video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
    #     frame_st.image(video_frame, use_column_width=True)
    #     blur = cv2.medianBlur(video_frame, 5)
    #     valor = read_barcodes(blur)
    #     st.write(valor)

        # if video_frame is not None:
        #     file_bytes = io.BytesIO(video_frame.getvalue())
        #     image = cv2.imdecode(np.frombuffer(file_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
        #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #     blur = cv2.medianBlur(gray, 5)
        #     valor = read_barcodes(blur)
        #     st.write(valor)

        #     # pil image to bytes
        #     # buf = io.BytesIO()
        #     # video_frame.save(buf, format='PNG')
        #     # file_bytes = io.BytesIO(buf.getvalue())

        #     if valor is not None:
        #         st.button('Inventariar bobina')
    # st.checkbox('')


    

    

    


def download_etiqueta(texto_qrcode: str, dados_bobina: pd.DataFrame) -> None:
    imagem_bobina_qr = qrcode.make(texto_qrcode, version=1, box_size=3, border=1)
    image_bytearray = io.BytesIO()
    imagem_bobina_qr.save(image_bytearray, format='PNG', name='qrcode.png')

    # qr = qrcode.QRCode(version=1, box_size=5, border=5)
    # qr = qr.add_data(texto_qrcode)
    # imagem_bobina_qr = qr.make(fit=True)
    # image_bytearray = io.BytesIO()

    # st.write(type(image_bytearray))
    # st.write(type(imagem_bobina_qr))


    if dados_bobina.loc['tipo_de_etiqueta'] == 'LIBERADO':
        wb = load_workbook('LIBERADO.xlsx')
        ws = wb.active
        # ws = wb['LIBERADO']
        img = Image_openpyxl(image_bytearray)
        ws.add_image(img,'F2')
        st.write(dados_bobina.astype(str))

        ft = Font(bold=True, size=48)

        ws['A2'] = dados_bobina.loc['sap'] 
        ws['A3'] = dados_bobina.loc['descricao'] 
        ws['A5'] = dados_bobina.loc['conferente'] 
        ws['A9'] = dados_bobina.loc['lote'] 
        ws['D9'] = dados_bobina.loc['data'] 
        ws['A18'] = str(dados_bobina.loc['quantidade'])
        ws['D18'] = dados_bobina.loc['tipo'].replace('BOBINA ALUMINIO ', '')

        ws['A18'].font = ft
      
        #Image.open(imagem_bobina_qr.save(image_bytearray, format='PNG', name='qrcode.PNG'))
        #img = Image.open(image_bytearray)
        #img = Image.open(image_bytearray.getvalue())
        #img = Image.open(imagem_bobina_qr)
        #img = Image.open(imagem_bobina_qr.save(image_bytearray, format='PNG'))
        #img = Image_openpyxl(image_bytearray.getvalue())
        #img = Image_openpyxl(imagem_bobina_qr)

    if dados_bobina.loc['tipo_de_etiqueta'] == 'BLOQUEADO':
        
        wb = load_workbook('BLOQUEADO.xlsx')
        ws = wb.active        
        #ws = wb['BLOQUEADO']
        img = Image_openpyxl(image_bytearray)
        ws.add_image(img,'A23')

        st.write(dados_bobina.astype(str))

        ws['A2'] = dados_bobina.loc['sap'] #codigo do produto
        ws['A3'] = dados_bobina.loc['quantidade'] #quantidade do produto
        ws['A5'] = dados_bobina.loc['lote'] #lote do produto
        ws['A13'] = dados_bobina.loc['data'] #data de entrada do produto

    wb.save('Etiqueta_download.xlsx')
    stream = BytesIO()
    wb.save(stream)
    towrite = stream.getvalue()
    b64 = base64.b64encode(towrite).decode()  # some strings

    # link para download e nome do arquivo
    linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="myfilename.xlsx">Download etiqueta</a>'
    st.markdown(linko, unsafe_allow_html=True)

    # st.subheader('Imagem do qrcode')
    # st.image(image_bytearray.getvalue())



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

            for bobina in lista_etiquetas:
                texto_expander = ''.join(('Lote: ', str(df_etiqueta_dia.loc[bobina]['lote']), ' Quantidade: ', str(df_etiqueta_dia.loc[bobina]['quantidade']), ' (', str(bobina), ')'))
                with st.expander(texto_expander):
                    texto_qrcode = ''
                    for colunas in df_etiqueta_dia.columns:
                        if colunas != 'tipo_de_etiqueta':
                            texto_qrcode = ''.join((texto_qrcode, str(df_etiqueta_dia.loc[bobina, colunas]), ','))
                            st.write(f'**{colunas}:** {df_etiqueta_dia.loc[bobina, colunas]}')

                    botao_download_etiqueta = st.button('Download etiqueta', key=str(bobina))
                    if botao_download_etiqueta:
                        download_etiqueta(texto_qrcode, df_bobinas.iloc[bobina])

    
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

    # if 'logado' not in st.session_state:
    #     st.session_state['logado'] = False

    # if st.session_state['logado'] == False:
    #     login_session_state()

    c1,c2 = st.sidebar.columns([1,1])
    c1.image('logo2.png', width=150)

    # st.sidebar.subheader('Bobinas')
    # telas_bobinas = ['Entrada de bobinas', 'Etiquetas', 'Inventário']
    # tela_bobina = st.sidebar.radio('Menu bobinas', telas_bobinas)

    # if st.session_state['logado'] == True:

    st.sidebar.subheader('Bobinas')
    telas_bobinas = ['Entrada de bobinas', 'Etiquetas', 'Inventário']
    tela_bobina = st.sidebar.radio('Menu bobinas', telas_bobinas)

    if tela_bobina == 'Entrada de bobinas':
        entrada_bobinas()

    if tela_bobina == 'Inventário':
        tela_inventario = st.sidebar.radio('Opções de inventário', ['Inserir', 'Visualizar']) #'Importar',

        if tela_inventario == 'Inserir':
            inserir_invetario()

    if tela_bobina == 'Etiquetas':
        etiquetas_bobinas()

        # botao_sair = st.sidebar.button('Sair')

        # if botao_sair:
        #     st.session_state['logado'] = False
        #     st.experimental_rerun()