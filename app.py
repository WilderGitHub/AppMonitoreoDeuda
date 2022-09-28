import PySimpleGUI as sg
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from junciones import *
#Archivo de parámetros, movimientos y palabras clave
#usuario = "rserdan"
#pasguor="789789++uiouio"
arch='goideuda 2022.xls'
menosEstas=['cve_debe_haber','cod_movimiento','esdeuda','DesembPtmo','',''] #'cod_moneda',
import re

#Aqui empezaría la onda
# tema
sg.theme('LightGrey1')
# el diseño

layout = [[sg.T("")],
          losInputs("Archivo: ","-GOI2-","GOI",34),
          [sg.Button("Hagamoslo", pad=((350, 0), 30), font='Arial 12', button_color=('black'))]]
# Creamos la ventana
window = sg.Window('Moni toreo Deuda Pendiente', layout, size=(750, 150))
# escuchamos los eventos
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == "Hagamoslo":
        bdBruto = leer(os.path.abspath(values["GOI"]))
        # todo a minusculas
        bdBruto.columns = map(str.lower, bdBruto.columns)
        # reducimos columnas 
        bdBruto=reducirColumnas(os.path.abspath(values["GOI"]),bdBruto)   
        bdBruto["esdeuda"] = bdBruto["glosa_comprob"].map(lambda x:esdeuda(x,acreedor,acreedorDesemb,debidoacreedor))
        bdDeuda=bdBruto[bdBruto["esdeuda"]==True]
        bdDeuda= bdDeuda[bdDeuda["cod_mayor"].isin(mayores)]
        if (bdDeuda.shape)[0] == 0:
            sg.Popup('Oe', 'Nuay movimiento oe')
        else:
        #print(bdDeuda.shape)
            bdDeuda["DesembAcreedor"]=bdBruto["glosa_comprob"].map(lambda x:extraeEntidades(x,acreedorDesemb))
            bdDeuda["DesembPtmo"]=bdBruto["glosa_comprob"].map(lambda x:extraeEntidades(x,ptmoDesemb))
            bdDeuda["DesembPtmoX"]=bdDeuda.apply(extraePtmoDesemb, axis=1)
            bdDeuda["DesembEn$us"]=bdBruto.apply(montoDesembolsado, axis=1)

            bdDeuda["ServicioAcreedor"]=bdBruto["glosa_comprob"].map(lambda x:extraeEntidades(x,acreedor))
            bdDeuda["ServicioPtmo"]=bdBruto["glosa_comprob"].map(lambda x:extraeEntidades(x,ptmo))
            bdDeuda["ServicioDeudor"]=bdBruto["glosa_comprob"].map(lambda x:extraeEntidades(x,deudor))
            
            bdDeuda["MonedaCapital"]=bdBruto["glosa_comprob"].map(lambda x:extraeMoneda(x,montos[0]+buscaMontos))
            bdDeuda["PagoCapitalMO"]=bdBruto["glosa_comprob"].map(lambda x:extraeMonto(x,montos[0]+buscaMontos))
            bdDeuda["MonedaIntereses"]=bdBruto["glosa_comprob"].map(lambda x:extraeMoneda(x,montos[1]+buscaMontos))
            bdDeuda["PagoInteresesMO"]=bdBruto["glosa_comprob"].map(lambda x:extraeMonto(x,montos[1]+buscaMontos))
            bdDeuda["MonedaComisiones"]=bdBruto["glosa_comprob"].map(lambda x:extraeMoneda(x,montos[2]+buscaMontos))
            bdDeuda["PagoComisionesMO"]=bdBruto["glosa_comprob"].map(lambda x:extraeMonto(x,montos[2]+buscaMontos))
            
            bdDeuda["PagoCapital$us"]=bdDeuda.apply(montoPagadoK, axis=1)
            #bdDeuda["PagoCapital$us"]=bdDeuda.apply(montoPagado("PagoCapitalMO","MonedaCapital"), axis=1)
            bdDeuda["PagoIntereses$us"]=bdDeuda.apply(montoPagadoI, axis=1)
            bdDeuda["PagoComisiones$us"]=bdDeuda.apply(montoPagadoC, axis=1)
            bdDeuda["Pagado"]=bdBruto["cod_mayor"].map(lambda x: "Pagado" if x == 10 else None)
            bdDeudaOK=bdDeuda.loc[:, ~bdDeuda.columns.isin(menosEstas)]
            
            nombre,ruta=nombrecito(bdDeudaOK,"fecha_dia")
            bdDeudaOK.to_excel(ruta+"/"+nombre+".xlsx", index=False)
            sg.Popup('Oe', 'Ya hemos generado el excel oe')    
            #print("Ya hemos generado el excel oe")
        