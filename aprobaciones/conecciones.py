from datetime import date,datetime, timedelta
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse,StreamingHttpResponse
from django.template.loader import render_to_string
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy,reverse
from django.core.files.storage import FileSystemStorage
from django.views.generic import ListView,CreateView
from django.views.generic.edit import UpdateView
from django.forms import ModelForm, Form, modelformset_factory, inlineformset_factory
from django.db.models import Q
from django.contrib import messages 
import csv,io,pymysql, math

@login_required
def EM_Buscar(request,ohost,oport,ouser,opass,odb):
    db = pymysql.connect(
        host=ohost,
        port=int(oport),
        user=ouser,
        passwd=opass,
        db=odb
    )
    cursor = db.cursor()

    sql = "select msr.referencia,msr.fecha,msr.ordenes_compra_id,sum(det.unidades),sum(det.costo),sum(det.impuesto),msr.costo_compra,msr.costo_iva,es.estado_desc "
    sql +=" from pruebas.com_entradamercaderiamsr msr inner join pruebas.com_entradamercaderiadet det on msr.referencia = det.referencia_id"
    sql +=" inner join inv_estado es on msr.estado_id  = es.id"
    sql +=" group by msr.referencia order by msr.referencia desc  limit 8;" 
    try:
        cursor.execute(sql)
        entradas = cursor.fetchall()
        # print(entradas)
    except Exception as err:
        print('hubo algun error')
        print(err)
        db.rollback()
        db.close()
        return list()

    return entradas


@login_required
def EM_Maestro(request,ohost,oport,ouser,opass,odb,codigo):
    db = pymysql.connect(
        host=ohost,
        port=int(oport),
        user=ouser,
        passwd=opass,
        db=odb
    )
    cursor = db.cursor()

    sql = "select msr.referencia,msr.fecha,msr.ordenes_compra_id,sum(det.unidades),sum(det.costo),sum(det.impuesto),msr.costo_compra,msr.costo_iva,es.estado_desc "
    sql += f" from {odb}.com_entradamercaderiamsr msr "
    sql += f" inner join {odb}.com_entradamercaderiadet det "
    sql += f"   on msr.referencia = det.referencia_id "
    sql += f" inner join {odb}.inv_estado es "
    sql += f"   on msr.estado_id = es.id "
    sql += f" where referencia = '{codigo}'"
    sql += f" group by msr.referencia; "
    try:
        cursor.execute(sql)
        OrdenCompra = cursor.fetchall()
        # print(entradas)
    except Exception as err:
        print('hubo algun error')
        print(err)
        db.rollback()
        db.close()
        return list()

    return OrdenCompra

@login_required
def EM_Detalle(request,ohost,oport,ouser,opass,odb,codigo):
    db = pymysql.connect(
        host=ohost,
        port=int(oport),
        user=ouser,
        passwd=opass,
        db=odb
    )
    cursor = db.cursor()
    print(codigo)
    # codigo,descripcion,unidades,costo,impuesto
    sql =  f"select  det.item_id,concat(prod.descripcion,' ',fam.descripcion,' ',mar.marca),det.unidades, det.costo, det.impuesto "
    sql += f"from {odb}.com_entradamercaderiadet det "
    sql += f"inner join  {odb}.com_entradamercaderiamsr msr "
    sql += f" on msr.referencia = det.referencia_id "
    sql += f"inner join  {odb}.inv_n4item item "
    sql += f" on det.item_id = item.id_n4 "
    sql += f"inner join  {odb}.inv_marcaitem mar "
    sql += f" on item.marca_id = mar.siglas "
    sql += f"inner join {odb}.inv_n3producto prod "
    sql += f" on item.producto_id = prod.id_n3 "
    sql += f"inner join {odb}.inv_n2familia fam "
    sql += f" on prod.familia_id = fam.id_n2 "
    sql += f"Where msr.referencia = '{codigo}';"
    try:
        cursor.execute(sql)
        detalles = cursor.fetchall()
        # print(detalles)
    except Exception as err:
        print('hubo algun error')
        print(err)
        db.rollback()
        db.close()
        return list()

    return detalles

@login_required
def EM_Actualizar(request,ohost,oport,ouser,opass,odb,codigo,estado):
    
    
    
    
    
    db = pymysql.connect(
        host=ohost,
        port=int(oport),
        user=ouser,
        passwd=opass,
        db=odb
    )

    Maestro = EM_Maestro(request,'127.0.0.1','3306','root','','pruebas',codigo)
    Detalles = EM_Detalle(request,'127.0.0.1','3306','root','','pruebas',codigo)


    CostoAdicional = float(Maestro[0][6])
    IvaAdicional = float(Maestro[0][7])

    prorrateoCosto = math.floor(float(CostoAdicional)) / float((len(Detalles) if len(Detalles)>0 else 1))
    prorrateoIva   = math.floor(float(IvaAdicional)) / float((len(Detalles) if len(Detalles)>0 else 1))
    # sobranteCosto  = CostoAdicional - (float((len(Detalles) if len(Detalles)>0 else 1)) * prorrateoCosto)
    sobranteCosto  = float(10)
    sobranteIva   = IvaAdicional   - (float((len(Detalles) if len(Detalles)>0 else 1)) * prorrateoIva)
    # print(len(Detalles))
    # print(Maestro[0][6])#Costo Adiccional
    # print(Maestro[0][7])#Iva Adiccional
    # print(prorrateoCosto)#Costo Adiccional
    # print(prorrateoIva)#Iva Adiccional
    

    primero = True

    if estado == '3':
        if primero:
            primero = False
            for i in Detalles:
                # print(i[0])#Codigo
                print(i[1])#Descripcion
                # print(i[2])#Cantidades
                print(i[3]+prorrateoCosto+sobranteCosto)#costo
                print(i[4]+prorrateoIva+sobranteIva)#Iva
                cursor = db.cursor()
                sql  = f"Update {odb}.com_entradamercaderiadet "
                sql += f" set costo = '{i[3]+prorrateoCosto+sobranteCosto}', "
                sql += f"     impuesto = '{i[4]+prorrateoIva+sobranteIva}'"
                sql += f" where referencia = '{codigo}' "
                sql += f"   and codigo = '{i[0]}'; "
                try:
                    cursor.execute(sql)
                    db.commit()
                    db.close()
                    return 'ok'
                except:
                    db.rollback()
                    db.close()
                    return 'error'

        else:
            for i in Detalles:
                # print(i[0])#Codigo
                print(i[1])#Descripcion
                # print(i[2])#Cantidades
                print(i[3]+prorrateoCosto)#costo
                print(i[4]+prorrateoIva)#Iva


    elif estado == '2':
        # print('rechazado')
        cursor = db.cursor()
        sql  = f"Update {odb}.com_entradamercaderiamsr "
        sql += f" set estado_id = {estado} "
        sql += f" where referencia = '{codigo}';"
        try:
            cursor.execute(sql)
            db.commit()
            db.close()
            return 'ok'
        except:
            db.rollback()
            db.close()
            return 'error'




@login_required
def OC_Buscar(request,ohost,oport,ouser,opass,odb):
    db = pymysql.connect(
        host=ohost,
        port=int(oport),
        user=ouser,
        passwd=opass,
        db=odb
    )
    cursor = db.cursor()

    sql =  " select msr.referencia, msr.fecha, sum(det.unidades), sum(det.costo), sum(det.impuesto), es.estado_desc "
    sql += f" from {odb}.com_ordencompramsr msr "
    sql += f" inner join {odb}.com_ordencompradet det "
    sql += " on msr.referencia = det.referencia_id "
    sql += f" inner join {odb}.inv_estado es "
    sql += " on msr.estado_id = es.id "
    sql += " group by msr.referencia  order by msr.referencia desc limit 8; "
    try:
        cursor.execute(sql)
        entradas = cursor.fetchall()
        # print(entradas)
    except Exception as err:
        print('hubo algun error')
        print(err)
        db.rollback()
        db.close()
        return list()

    return entradas

@login_required
def OC_Maestro(request,ohost,oport,ouser,opass,odb,codigo):
    db = pymysql.connect(
        host=ohost,
        port=int(oport),
        user=ouser,
        passwd=opass,
        db=odb
    )
    cursor = db.cursor()

    sql =  f" select msr.referencia, msr.fecha, sum(det.unidades), sum(det.costo), sum(det.impuesto), es.estado_desc "
    sql += f" from {odb}.com_ordencompramsr msr "
    sql += f" inner join {odb}.com_ordencompradet det "
    sql += f"   on msr.referencia = det.referencia_id "
    sql += f" inner join {odb}.inv_estado es "
    sql += f"   on msr.estado_id = es.id "
    sql += f" where referencia = '{codigo}'"
    sql += f" group by msr.referencia; "
    try:
        cursor.execute(sql)
        OrdenCompra = cursor.fetchall()
        # print(entradas)
    except Exception as err:
        print('hubo algun error')
        print(err)
        db.rollback()
        db.close()
        return list()

    return OrdenCompra

@login_required
def OC_Detalle(request,ohost,oport,ouser,opass,odb,codigo):
    db = pymysql.connect(
        host=ohost,
        port=int(oport),
        user=ouser,
        passwd=opass,
        db=odb
    )
    cursor = db.cursor()
    print(codigo)
    # codigo,descripcion,unidades,costo,impuesto
    sql =  f"select  det.item_id,concat(prod.descripcion,' ',fam.descripcion,' ',mar.marca),det.unidades, det.costo, det.impuesto "
    sql += f"from {odb}.com_ordencompradet det "
    sql += f"inner join  {odb}.com_ordencompramsr msr "
    sql += f" on msr.referencia = det.referencia_id "
    sql += f"inner join  {odb}.inv_n4item item "
    sql += f" on det.item_id = item.id_n4 "
    sql += f"inner join  {odb}.inv_marcaitem mar "
    sql += f" on item.marca_id = mar.siglas "
    sql += f"inner join {odb}.inv_n3producto prod "
    sql += f" on item.producto_id = prod.id_n3 "
    sql += f"inner join {odb}.inv_n2familia fam "
    sql += f" on prod.familia_id = fam.id_n2 "
    sql += f"Where msr.referencia = '{codigo}';"
    try:
        cursor.execute(sql)
        detalles = cursor.fetchall()
        # print(detalles)
    except Exception as err:
        print('hubo algun error')
        print(err)
        db.rollback()
        db.close()
        return list()

    return detalles

@login_required
def OC_Actualizar(request,ohost,oport,ouser,opass,odb,codigo,estado):
    db = pymysql.connect(
        host=ohost,
        port=int(oport),
        user=ouser,
        passwd=opass,
        db=odb
    )
    cursor = db.cursor()
    sql  = f"Update {odb}.com_ordencompramsr "
    sql += f" set estado_id = {estado} "
    sql += f" where referencia = '{codigo}';"
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
        return 'ok'
    except:
        db.rollback()
        db.close()
        return 'error'


