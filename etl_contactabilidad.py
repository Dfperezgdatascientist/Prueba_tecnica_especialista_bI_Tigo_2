### Modulos
# Tratamiento de datos
# ==============================================================================
import numpy as np
import pandas as pd
import re
import datetime 
from sklearn.datasets import make_classification
# Configuración warnings
# ==============================================================================
import warnings
warnings.filterwarnings('once')
warnings.simplefilter('ignore', (DeprecationWarning))
pd.set_option('display.float_format', lambda x: '%.5f' % x)
pd.set_option('display.max_rows', 500)
pd.options.display.max_columns = 120

#### Funciones
# Limpieza, carecteres especiales y signos de puntuacion
def limpieza_basica(body):
    body = body.lower()
    body = re.sub(" \d+",' ', body) #Eliminar numeros
    body = re.sub('[^a-z ]',' ', body) #quitar numeros dentro de palabras
    body = re.sub('\[#*.>=\]','',body) # Eliminar caracteres 
    #body = re.sub('[%s]' %re.escape(string.punctuation),' ', body) # Eliminar signos puntuacion
    body= re.sub(r"[\r\n]+",' ', body)
    body= re.compile(r'\bLiza\b').sub(' ', body)
    body=re.sub("\s\s+" , " ", body)
    body= body.strip()
    return body
limpiar = lambda x: limpieza_basica(x)

#### Carga de base N1
df_n1= pd.read_csv(r'C:\Users\Daniel\Documents\GitHub\Bases\Base N1 202302.csv',sep='|')
#### Carga de base N2
df_n2= pd.read_csv(r'C:\Users\Daniel\Documents\GitHub\Bases\Base N2 202302.csv',sep='|')

#### etl base n1
df_n1_etl_1=df_n1[~(df_n1['Id Registro'].isna())]# Quitamos callid vacios
df_n1_etl_1.rename(columns = {'Id Registro':'CALLID'}, inplace = True)
df_n1_etl_1['fecha_registro_2']=pd.to_datetime(df_n1_etl_1['Fecha Registro']+' '+df_n1_etl_1['Hora Registro'],format='%Y/%m/%d %H:%M:%S',errors='coerce')#datetime.date.today()
df_n1_etl_1['anio_mes'] = df_n1_etl_1['fecha_registro_2'].dt.strftime('%Y%m')
df_n1_etl_2=df_n1_etl_1.sort_values(['CALLID','fecha_registro_2'],ascending=[True,True]).groupby('CALLID').head(1)

#### etl base n2
df_n2['fecha_2']=pd.to_datetime(df_n2['Fecha']+' '+df_n2['Hora'],format='%d/%m/%Y %H:%M:%S',errors='coerce')#datetime.date.today()
df_n2['anio_mes_2'] = df_n2['fecha_2'].dt.strftime('%Y%m') 
df_n2_etl_1=df_n2.sort_values(['CALLID','fecha_2'],ascending=[True,True]).groupby('CALLID').head(1)
df_n2_etl_1.rename(columns = {'Asesor':'Asesor_call','Negocio':'Negocio_call','Gerencia':'Gerencia_call'}, inplace = True)
#### Unir bases
BD_funnel_consol= df_n1_etl_2[['CALLID','Telefono', 'Nombre usuario', 'Id Oferta',
       'Descripcion Oferta', 'Descripcion Opcional', 'Codigo de resultado',
       'Fecha efectiva', 'Hora efectiva', 'Duracion', 'Asesor', 'Jobname',
       'Correo', 'DescSolicitudCliente', 'Fecha primer intento',
       'Hora primer intento', 'Gerencia', 'Negocio', 'Medio Pauta', 'fecha_registro_2', 'anio_mes']].merge(df_n2_etl_1[['CALLID', 'ANI', 'Asesor_call', 'Duracion_Seg', 'Piloto', 'Nivel1',
       'Nivel2', 'Nivel3', 'Nivel4', 'CodFinalizacion', 'Estado', 'DNIS','Negocio_call', 'Linea', 'BU', 'Gerencia_call', 'Origen','fecha_2', 'anio_mes_2']], on=['CALLID'],how='left')

#### Construcción de variables
BD_funnel_consol['Medio_Pauta_2'] = BD_funnel_consol['Medio Pauta'].apply(limpiar)
BD_funnel_consol['Medio_Pauta_pareto'] = np.where((BD_funnel_consol['Medio_Pauta_2'] =='sem') , 'sem',
                                              np.where((BD_funnel_consol['Medio_Pauta_2'] == 'facebook'), 'facebook',
                                                       np.where((BD_funnel_consol['Medio_Pauta_2'] == 'abandono ecommerce home'), 'abandono ecommerce home',
                                                                np.where((BD_funnel_consol['Medio_Pauta_2'] == 'masiv'), 'masiv',
                                                                         np.where((BD_funnel_consol['Medio_Pauta_2'] == 'portal'), 'portal','otro')))))


BD_funnel_consol['efectivos'] = np.where((BD_funnel_consol['Nivel1'] =='VENTA') , 'SI','NO')
BD_funnel_consol['contacto_efectivo'] = np.where((BD_funnel_consol['Estado'] =='Atendido') , 'SI','NO')
BD_funnel_consol['llamada_avandonada'] = np.where((BD_funnel_consol['CodFinalizacion'] =='Abandonada') , 'SI','NO')
BD_funnel_consol.to_csv(r"./funnel_consolidado.csv")

del df_n1, df_n2, df_n1_etl_1, df_n2_etl_1, BD_funnel_consol
                                                                         

