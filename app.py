######################################################################################################
                                           #Introduaao
######################################################################################################



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

# import asyncio
# import logging
import queue
# import threading
# import urllib.request
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
st.set_page_config(
     page_title="Inventario",
)

def read_barcodes(frame):
#     try:
        barcodes = decode(frame)
        for barcode in barcodes:
            x, y , w, h = barcode.rect        #1
            barcode_info = barcode.data.decode('utf-8')             
            return barcode_info
#     except:
#         return None

# Configurando o acesso ao mongodb
myclient = pymongo.MongoClient("mongodb://192.168.81.128:27017/")
mydb = myclient["mydatabase"]

# upload de imagem para mongodb
images = mydb.images

telas = ['Inserir item no inventario', 'Atualizar item no inventario', 'Visualizar inventarios']
tela = st.sidebar.radio('Menu', telas)



######################################################################################################
                               #Funaoes
######################################################################################################

def qr_code_detector():

    class OpenCVVideoProcessor(VideoProcessorBase):

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
		    
#     webrtc_ctx = webrtc_streamer(
#         key="opencv-filter",
#         mode=WebRtcMode.SENDRECV,
#         rtc_configuration=RTC_CONFIGURATION,
#         video_processor_factory=OpenCVVideoProcessor,
#         async_processing=True,
#         media_stream_constraints={"video": True, "audio": False},
#     )
    #st.camera_input('')
    webrtc_ctx = webrtc_streamer(
        key="video-sendonly",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=OpenCVVideoProcessor,
#         async_processing=True,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True},
    )

    st.button('teste')
    if webrtc_ctx.video_receiver:
        st.write('estou aqui')
        while True:
    
            if webrtc_ctx.video_receiver:
                #st.write('deu bom 1')
                try:
                    video_frame = webrtc_ctx.video_receiver.get_frame(timeout=1)
                    #st.write('deu bom 2')
                except queue.Empty:
                    #logger.warning("Queue is empty. Abort.")
                    st.write('deu merda 1')
                    break
    		
                img_rgb = video_frame.to_ndarray(format="rgb24")
                #image = cv2.imdecode(np.frombuffer(img_rgb, np.uint8), cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
                blur = cv2.medianBlur(gray, 5)
                valor = read_barcodes(blur)
                st.write(valor)
    #             file_bytes = io.BytesIO(img_rgb.getvalue())
    #             image = cv2.imdecode(np.frombuffer(file_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
    #             valor = read_barcodes(image)
                if valor != None:
                    st.write(valor)
                    st.image(img_rgb)
                    break
                    
            else:
                st.write('deu merda 0')
                #logger.warning("AudioReciver is not set. Abort.")
                break
		
#     if webrtc_ctx.video_processor:
#         image_qr = webrtc_ctx.video_processor._imagem
#         st.write(image_qr)
#         valor = read_barcodes(image_qr)
#         st.write(valor)



st.title('Inventario Ambev - LM :memo:')
if tela == 'Inserir item no inventario':
    st.subheader('Formulario')

    with st.form(key='myform'):
        st.text_input('data do inventario') # data
        st.text_input('empresa')
        st.text_input('Unidade') #latas minas 
        st.text_input('Numero do bem')
        st.text_input('situacao') #opcoes:
        st.text_input('Descricao do ativo')
        st.text_input('loca/departamento')
        st.text_input('Responsavel pela localizacao')
        st.text_input('Numero TAG/Paleta')
        st.text_input('Turnos para uso do bem') #opcoes a,b,c,todos a e b, a e c, b e c
        st.text_input('data da aquisicao') #data
        st.text_input('Marca')
        st.text_input('Modelo')
        st.text_input('Numero de serie')
        st.text_input('Quantidade')

        submit_button = st.form_submit_button(label='Submit')

    st.write('TAG do equipamento')
    im1 = st.file_uploader('Selecione a foto da TAG')
    if im1 != None:
        st.image(io.BytesIO(im1.getvalue()))
        st.button('Confirma envio da foto da TAG?')

    st.write('Foto do equipamento')
    im2 = st.file_uploader('Selecione a foto do equipamento')
    if im2 != None:
        st.image(io.BytesIO(im2.getvalue()))
        st.button('Confirma envio da foto do equipamento?')
       

if tela == 'Visualizar inventarios':
#     video_frame = st.file_uploader('Selecione a foto do equipamento')
    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    qr_code_detector()

#     if video_frame is not None:
#         file_bytes = io.BytesIO(video_frame.getvalue())
#         image = cv2.imdecode(np.frombuffer(file_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         blur = cv2.medianBlur(gray, 5)
#         valor = read_barcodes(blur)
#         st.write(valor)
