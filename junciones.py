# JUNCIONES en modulo diferente oe
import os
import re
import PySimpleGUI as sg#funciones
from dbfread import DBF
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


casosEspeciales=['BID','CAF','IDA']
mayores = [10,381,404,406]
montos=['CAPITAL ','INTERESES ','COMISIONES ']
desAcree=['DESEMBOLSO DEL? ','(?= PR.STAMO)']
desPtmo=['POR DESEMBOLSO DE \w+ PRÉSTAMO ',' ']

akey=['PAGO A ','(?= PRÉSTAMO)']
pkey=['PRÉSTAMO ',' VCTO.']
dkey=['POR CUENTA DE ',' ,']

buscaMontos = '(\w+) ((\w+)($|\S+))'
buscaEntidades ='(.+?)'

buscaEntidades1 ='((.+?) (.+?)|(.+?))'

acreedorDesemb=desAcree[0]+buscaEntidades+desAcree[1]
ptmoDesemb=desPtmo[0]+buscaEntidades1+desPtmo[1]

acreedor=akey[0]+buscaEntidades+akey[1]
ptmo=pkey[0]+buscaEntidades+pkey[1]
deudor=dkey[0]+buscaEntidades+dkey[1]


def losInputs(nombreCampo,inputKey,fileKey, espacio):
    fila=[sg.Text(nombreCampo),
    sg.Input(key=inputKey, 
        change_submits=True, 
        pad=((espacio, 5), 5), 
        size=(80, 1)),
    sg.FileBrowse(key=fileKey)]
    return fila
def getExtension(archivo):
    extension = os.path.splitext(archivo)[1]
    return extension
def leer(nombreArchivo):
    if getExtension(nombreArchivo) == '.dbf':
        table = DBF(nombreArchivo, encoding='latin', load=True)
        return pd.DataFrame(iter(table))
    else:
        #para los que no son dbf
        return pd.read_excel(nombreArchivo)
def reducirColumnas (nombreArchivo,ddff):
        if getExtension (nombreArchivo) == '.dbf':
            bdReducida = ddff.loc[:, ('fecha_dia', 'cve_debe_h', 'monto_mo','factor_conv_mo_mn',
                                     'cod_moneda', 'cod_movimi', 'nom_movimi',
                                         'monto_mn', 'glosa_comp', 'nro_compro', 'cod_mayor')]
        else:

            bdReducida = ddff.loc[:, ('fecha_dia', 'cve_debe_haber', 'monto_mo','factor_conv_mo_mn',
                                     'cod_moneda', 'cod_movimiento', 'nom_movimiento',
                                         'monto_mn', 'glosa_comprob', 'nro_comprob', 'cod_mayor')]
        return bdReducida

def esdeuda(texto,criterio1,criterio2):
    if extraeEntidades(texto,criterio1) or extraeEntidades(texto,criterio2):
        return True
    else:
        return False

def extraeMonto(texto,key):
    x = re.findall(key, texto)
    if x:
        xx=x[0][1].replace('.','').replace(',','.').replace(';','')
        try:
            float(xx)
        except:
            monto="algo"
        else:
            monto=float(xx)
        #y=[x[0][0],float(xx)]
        return monto

def extraeMoneda(texto,key):
    x = re.findall(key, texto)
    if x:
        try:
            x[0][0]
        except:
            moneda="---"
        else:
            moneda=x[0][0]
        return moneda
    
def extraeEntidades(texto,key):
    x = re.findall(key, texto)
    if x:
        if x[0]:
            return str(x[0])
        else:
            return "nd"

def extraeEntidadPtmoDesemb(texto,key,flag):
    x = re.findall(key, texto)
    if x:
        if x[0]:
            if flag==1:
                return str(x[0][1])
            else:
                return str(x[0][0])
        else:
            return "nd"



def extraePtmoDesemb(x):
    if x['DesembAcreedor'] in casosEspeciales:
        return extraeEntidadPtmoDesemb(x['glosa_comprob'],ptmoDesemb,1)
    else:
        return extraeEntidadPtmoDesemb(x['glosa_comprob'],ptmoDesemb,0)
    
def separa(s):
    letras='([A-Z])'
    numeros='(\d+)'
    x = re.findall(letras, s)
    y = re.findall(numeros, s)
    xx=''.join(x) if x else 'nuay'
    yy=int(y[0]) if y else 'nuay'
    return [xx,yy]


def montoDesembolsado (x):
    if x['cve_debe_haber']=="D":
        #normalmente es Dólares, pero podrían haber otras monedas, hay que generalizar la fórmula oe.
        return round(x['monto_mn']/x['factor_conv_mo_mn'],2)
def montoPagadoK(x):
    if x['cve_debe_haber']=="H":
        try:
            x["PagoCapitalMO"]*x['factor_conv_mo_mn']
        except:
            return None
        else:    
            return round(x["PagoCapitalMO"]*x['factor_conv_mo_mn']/6.86,2)
        
def montoPagadoI(x):
    if x['cve_debe_haber']=="H":
        try:
            x["PagoInteresesMO"]*x['factor_conv_mo_mn']
        except:
            return None
        else:    
            return round(x["PagoInteresesMO"]*x['factor_conv_mo_mn']/6.86,2)   
def montoPagadoC(x):
    if x['cve_debe_haber']=="H":
        try:
            x["PagoComisionesMO"]*x['factor_conv_mo_mn']
        except:
            return None
        else:    
            return round(x["PagoComisionesMO"]*x['factor_conv_mo_mn']/6.86,2)   
def nombrecito(df,campofecha):
    nombre = "MoniDeuda_"+df[campofecha].min().strftime("%d%b") + "-"+df[campofecha].max(
    ).strftime("%d%b")+"("+pd.Timestamp.now().strftime("%d%b%H%M")+")"
    # get current directory
    path = os.getcwd()
    #print("Current Directory", path)
    # parent directory
    parent = os.path.dirname(path)
    return nombre,parent