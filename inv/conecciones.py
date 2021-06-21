# import MySQLdb as pymysql
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
from . import models, forms
from vta.apoyo import reino
from usuarios.models import LoggedInUser
from django.db.models import Q
from django.contrib import messages 
import csv,io
from vta.models import Facturamsr,Facturadet
from com.models import EntradaMercaderiaMsr,EntradaMercaderiaDet 

def insertar_traslado(suc,ref):
    print('Entre a la funcion')
    sucursal = models.Sucursal.objects.get(siglas = suc)
    detalles = models.TrasladoDet.objects.filter(referencia = ref)
    cabecera = models.TrasladoMsr.objects.get(referencia = ref)
    print('detalle')
    print(detalles)
    print('cabecera')
    print(cabecera)
    db = pymysql.connect(
        host=sucursal.ipaddress,
        port=int(sucursal.port),
        user=sucursal.usuario,
        passwd=sucursal.password,
        db=sucursal.database
    )
    cursor=db.cursor()
    print('cree el cursor')
    sql = "Insert into %s.inv_trasladomsr(referencia,fecha,nota,estado_id,sucursal_id,sucursald_id) values('%s','%s','%s','%s','%s','%s') ON DUPLICATE KEY UPDATE referencia ='%s',fecha = '%s',nota = '%s',estado_id = %s,sucursal_id = '%s',sucursald_id = '%s'"%(
        sucursal.database,
        cabecera.referencia,
        cabecera.fecha,
        cabecera.nota,
        4,#cabecera.estado.id,#
        cabecera.sucursal.siglas,
        cabecera.sucursalD.siglas,
        cabecera.referencia,
        cabecera.fecha,
        cabecera.nota,
        4,#cabecera.estado.id,#
        cabecera.sucursal.siglas,
        cabecera.sucursalD.siglas
    )
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        print('pude crearle el maestro')
    except Exception as err:
        print('error al crear el maestro')
        print(err)
        db.rollback()
        db.close()
        return 'error'
    # grabando el detalle del traslado
    for item in detalles:
        sql = "Insert into %s.inv_trasladodettemp(cantidad,costo,bodegaD_id,bodegaO_id,estado_id,item_id,referencia_id) values(%s,%s,'%s','%s','%s','%s','%s') ON DUPLICATE KEY UPDATE  cantidad = %s, costo = %s, bodegaD_id = '%s', bodegaO_id='%s', estado_id = %s, item_id = '%s', referencia_id = '%s' "%(
            sucursal.database,
            item.cantidad,
            item.costo,
            item.bodegaD.id_bodega,
            item.bodegaO.id_bodega,
            4,
            item.item.id_n4,
            item.referencia.referencia,
            item.cantidad,
            item.costo,
            item.bodegaD.id_bodega,
            item.bodegaO.id_bodega,
            4,
            item.item.id_n4,
            item.referencia.referencia
        )
        print(sql)
        try:
            print('ok')
            cursor.execute(sql)
            db.commit()
            db.close()
            return 'ok'
        except Exception as err:
            print('error')
            print(err)
            db.rollback()
            db.close()
            return 'error'

def insertar_rubro(suc,id_n1):
    print('entre a la funcion')
    print(suc)
    print(id_n1)
    rubro = models.N1Rubro.objects.get(pk = id_n1)
    sucursal = models.Sucursal.objects.get(siglas = suc)
    db = pymysql.connect(
        host=sucursal.ipaddress,
        port=int(sucursal.port),
        user=sucursal.usuario,
        passwd=sucursal.password,
        db=sucursal.database
    )
    cursor = db.cursor()
    sql = "INSERT INTO %s.inv_n1rubro(id_n1,descripcion,codigo_sac) values('%s','%s','%s') ON DUPLICATE KEY UPDATE id_n1 = '%s', descripcion = '%s', codigo_sac = '%s'  "%(
            sucursal.database,
            rubro.id_n1,
            rubro.descripcion,
            rubro.codigo_sac,
            rubro.id_n1,
            rubro.descripcion,
            rubro.codigo_sac
        )
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
        return 'ok'
    except:
        db.rollback()
        db.close()
        return 'error'

def insertar_familia(suc,id_n2):
    familia = models.N2Familia.objects.get(pk = id_n2)
    sucursal = models.Sucursal.objects.get(siglas = suc)
    db = pymysql.connect(
        host = sucursal.ipaddress,
        port = int(sucursal.port),
        user = sucursal.usuario,
        passwd = sucursal.password,
        db = sucursal.database
    )
    cursor = db.cursor()
    sql = "INSERT INTO %s.inv_n2familia(id_n2,descripcion,codigo,rubro_id) values ('%s','%s','%s','%s') ON DUPLICATE KEY UPDATE id_n2 = '%s', descripcion = '%s', codigo = '%s', rubro_id = '%s'  "%(
            sucursal.database,
            familia.id_n2,
            familia.descripcion,
            familia.codigo,
            familia.rubro.id_n1,
            familia.id_n2,
            familia.descripcion,
            familia.codigo,
            familia.rubro.id_n1
        )
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
        print('ok')
        return 'ok'
    except  Exception as err:
        db.rollback()
        db.close()
        print(err)
        print('error')
        return 'error'
    
def insertar_um(suc,id_um):
    um = models.Um.objects.get(pk = id_um)
    sucursal = models.Sucursal.objects.get(siglas = suc)
    db = pymysql.connect(
        host = sucursal.ipaddress,
        port = int(sucursal.port),
        user = sucursal.usuario,
        passwd = sucursal.password,
        db = sucursal.database
    )
    cursor = db.cursor()
    sql = "INSERT INTO %s.inv_um(id_um, nombre) values('%s','%s') ON DUPLICATE KEY UPDATE id_um = '%s', nombre = '%s' "%(
            sucursal.database,
            um.id_um,
            um.nombre,
            um.id_um,
            um.nombre
        )
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
        return 'ok'
    except:
        db.rollback()
        db.close()
        return 'error'

def insertar_producto(suc,id_n3):
    producto = models.N3Producto.objects.get(pk  = id_n3)
    sucursal = models.Sucursal.objects.get(siglas = suc)
    print(sucursal)
    db = pymysql.connect(
        host = sucursal.ipaddress,
        port = int(sucursal.port),
        user = sucursal.usuario,
        passwd = sucursal.password,
        db = sucursal.database
    )
    cursor = db.cursor()

    sql = "INSERT INTO %s.inv_n3producto(id_n3,descripcion,codigo,oem,cod_fabrica,sac,minimo,maximo,descontinuado,entero,naturaleza,exo_rubro_id,familia_id,medida_id) values('%s','%s','%s','%s','%s','%s',%s,%s,'%s','%s','%s',%s,'%s','%s') ON DUPLICATE KEY UPDATE id_n3 = '%s' ,descripcion = '%s' ,codigo = '%s' ,oem = '%s' ,cod_fabrica = '%s' ,sac = '%s',minimo = %s ,maximo = %s ,descontinuado = '%s' ,entero = '%s' ,naturaleza = '%s',exo_rubro_id = %s,familia_id= '%s',medida_id= '%s'"%(
        sucursal.database,
        producto.id_n3,
        producto.descripcion,
        producto.codigo,
        producto.oem,
        producto.cod_fabrica,
        producto.sac,
        producto.minimo,
        producto.maximo,
        producto.descontinuado,
        producto.entero,
        producto.naturaleza,
        producto.exo_rubro.id,
        producto.familia.id_n2,
        producto.medida.id_um,
        producto.id_n3,
        producto.descripcion,
        producto.codigo,
        producto.oem,
        producto.cod_fabrica,
        producto.sac,
        producto.minimo,
        producto.maximo,
        producto.descontinuado,
        producto.entero,
        producto.naturaleza,
        producto.exo_rubro.id,
        producto.familia.id_n2,
        producto.medida.id_um
    )
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as err:
        db.rollback()
        print('error')
        print(err)
        return ('err')
    
    print('guardo producto proceder a guardar las relaciones muchos a muchos')
    try:
        sucursal2 = models.Sucursal.objects.get(siglas = 'DU')
        db2 = pymysql.connect(
            host = sucursal2.ipaddress,
            port = int(sucursal2.port),
            user = sucursal2.usuario,
            passwd = sucursal2.password,
            db = sucursal2.database
        )
        cursor2 = db2.cursor()
        #conectandome desde el local para leer
        sql = "select * from %s.inv_n3producto_aplicacion where n3producto_id = '%s'"%(
            sucursal2.database,
            producto.id_n3
        )
        #ejecutando la tabla intermedia desde python
        print(sql)
        cursor2.execute(sql)
        intermedios = cursor2.fetchall()
        print(intermedios)

        #guardando cada respuesta a la otra sucursal
        for aplicaciones in intermedios:
            id = aplicaciones[0]
            producto_id = aplicaciones[1]
            modelovehiculo_id = aplicaciones[2]
            sql = "insert into %s.inv_n3producto_aplicacion(n3producto_id,modelovehiculo_id) values('%s','%s');"%(
                sucursal.database,
                producto_id,
                modelovehiculo_id
            )
            print(sql)
            cursor.execute(sql)
        db.commit()
        db.close()
        print('ok')
        return 'ok'
    except Exception as err:
        print(err)
        print('error')
        db.rollback()
        db.close()
        return 'err'

def insertar_marcaitem(suc,sigla):
    marcaitem = models.MarcaItem.objects.get(siglas = sigla)
    sucursal = models.Sucursal.objects.get(siglas = suc)
    db = pymysql.connect(
        host = sucursal.ipaddress,
        port = int(sucursal.port),
        user = sucursal.usuario,
        passwd = sucursal.password,
        db = sucursal.database
    )
    cursor = db.cursor()
    sql = "INSERT INTO %s.inv_marcaitem(siglas, marca) values('%s','%s') ON DUPLICATE KEY UPDATE siglas = '%s', marca = '%s' "%(
            sucursal.database,
            marcaitem.siglas,
            marcaitem.marca,
            marcaitem.siglas,
            marcaitem.marca
        )
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
        return 'ok'
    except Exception as err:
        print(err)
        db.rollback()
        db.close()
        return 'error'

def insertar_item(suc,sigla,boo):
    if boo:
        item = models.N4Item.objects.get(pk = sigla)
        sucursal = models.Sucursal.objects.get(siglas = suc)
        db = pymysql.connect(
            host = sucursal.ipaddress,
            port = int(sucursal.port),
            user = sucursal.usuario,
            passwd = sucursal.password,
            db = sucursal.database
        )
        cursor = db.cursor()
        sql = "INSERT INTO %s.inv_n4item(id_n4,descripcion,precio,cod_anterior,Cod_barra,sac,cantidad_impuesto,minimo,maximo,descontinuado,ExoTipo_id,marca_id,n3_id) values('%s','%s',%s,'%s','%s','%s',%s,%s,%s,'%s','%s','%s','%s') ON DUPLICATE KEY UPDATE id_n4 = '%s',descripcion = '%s',precio = %s,cod_anterior = '%s',Cod_barra ='%s' ,sac = '%s',cantidad_impuesto = %s,minimo=%s,maximo=%s,descontinuado='%s',ExoTipo_id= '%s',marca_id= '%s',n3_id='%s' "%(
                sucursal.database,
                item.id_n4,
                item.descripcion,
                item.precio,
                item.cod_anterior,
                item.Cod_barra,
                item.sac,
                item.cantidad_impuesto,
                item.minimo,
                item.maximo,
                item.descontinuado,
                item.ExoTipo_id,
                item.marca_id,
                item.n3_id,
                item.id_n4,
                item.descripcion,
                item.precio,
                item.cod_anterior,
                item.Cod_barra,
                item.sac,
                item.cantidad_impuesto,
                item.minimo,
                item.maximo,
                item.descontinuado,
                item.ExoTipo_id,
                item.marca_id,
                item.n3_id
            )
        print(sql)
        try:
            cursor.execute(sql)
            db.commit()
            print('ok al insertar item')
        except Exception as err:
            print(err)
            print('error')
            db.rollback()
            db.close()
            return 'error'
        db.close()
        return 'ok'
    else:
        item = models.N4Item.objects.get(pk = sigla)
        sucursal = models.Sucursal.objects.get(siglas = suc)
        db = pymysql.connect(
            host = sucursal.ipaddress,
            port = int(sucursal.port),
            user = sucursal.usuario,
            passwd = sucursal.password,
            db = sucursal.database
        )
        cursor = db.cursor()
        sql = "INSERT INTO %s.inv_n4item(id_n4,descripcion,precio,cod_anterior,Cod_barra,sac,cantidad_impuesto,minimo,maximo,descontinuado,ExoTipo_id,marca_id,n3_id) values('%s','%s',%s,'%s','%s','%s',%s,%s,%s,'%s','%s','%s','%s') ON DUPLICATE KEY UPDATE id_n4 = '%s',descripcion = '%s',precio = %s,cod_anterior = '%s',Cod_barra ='%s' ,sac = '%s',cantidad_impuesto = %s,minimo=%s,maximo=%s,descontinuado='%s',ExoTipo_id= '%s',marca_id= '%s',n3_id='%s' "%(
                sucursal.database,
                item.id_n4,
                item.descripcion,
                item.precio,
                item.cod_anterior,
                item.Cod_barra,
                item.sac,
                item.cantidad_impuesto,
                item.minimo,
                item.maximo,
                item.descontinuado,
                item.ExoTipo_id,
                item.marca_id,
                item.n3_id,
                item.id_n4,
                item.descripcion,
                item.precio,
                item.cod_anterior,
                item.Cod_barra,
                item.sac,
                item.cantidad_impuesto,
                item.minimo,
                item.maximo,
                item.descontinuado,
                item.ExoTipo_id,
                item.marca_id,
                item.n3_id
            )
        print(sql)
        try:
            cursor.execute(sql)
            db.commit()
            # db.close()
            print('ok al insertar item')
        except Exception as err:
            print(err)
            print('error')
            db.rollback()
            db.close()
            return 'error'

        #actualizandole los  precios
        precios = models.Precio.objects.all()
        for precio in precios:
            sql = "INSERT INTO %s.inv_n4itemxprecio(item_id,precio_id,valor) values('%s','%s',%s) ON DUPLICATE KEY UPDATE item_id = '%s', precio_id = '%s', valor = %s"%(
                sucursal.database,
                sigla,
                precio.id_precio,
                item.precio,
                sigla,
                precio.id_precio,
                item.precio
            )
            print(sql)
            try:
                cursor.execute(sql)
                db.commit()
                print('Ok')
            except Exception as err:
                print('Mensaje')
                print(err)
                print('error')
                db.rollback()
                return 'error'

        #Creo Existencias
        bodegas = models.Bodega.objects.all()
        for bodega in bodegas:
            sql = "INSERT INTO %s.inv_existenciabodega(cantidad,bodega_id,item_id) values(%s,'%s','%s') ON DUPLICATE KEY UPDATE cantidad = %s, bodega_id = '%s' ,item_id = '%s' "%(
                sucursal.database,
                0,
                bodega.id_bodega,
                sigla,
                0,
                bodega.id_bodega,
                sigla
            )
            print(sql)
            try:
                cursor.execute(sql)
                db.commit()
                print('ok')
            except Exception as err:
                print('Mensaje')
                print(err)
                print('error')
                db.rollback()
                db.close()
                return 'error'

        #Kardex
        sql = "INSERT INTO %s.inv_kardex (fecha,referencia,item_id,sucursal_id,entrada,salida,existencia,debe,haber,saldo,costounitario) values('%s','%s','%s','%s',0,0,0,0,0,0,0) ON DUPLICATE KEY UPDATE fecha = '%s', referencia = '%s', item_id = '%s', sucursal_id = '%s'"%(
            sucursal.database,
            date.today().strftime('%Y%m%d'),
            'Apertura',
            sigla,
            'DU',
            date.today().strftime('%Y%m%d'),
            'Apertura',
            sigla,
            'DU'
        )
        print(sql)
        try:
            cursor.execute(sql)
            db.commit()
            print('ok')
        except Exception as err:
            print('error')
            print(err)
            db.rollback()
            db.close()
            return 'error'

        #Item_Costo
        sql = "Insert into %s.inv_item_costo(item_id,costo,existencia,saldo) values('%s',0,0,0) ON DUPLICATE KEY UPDATE item_id = '%s'"%(
            sucursal.database,
            sigla,
            sigla
        )
        print(sql)
        try:
            cursor.execute(sql)
            db.commit()
            print('ok')
        except Exception as err:
            print('error')
            print(err)
            db.rollback()
            return 'Error'

        #Item_Costo_Historico
        sql = "Insert into %s.inv_item_costo_historico(item_id,costo,existencia,fecha,saldo) values('%s',0,0,%s,0) ON DUPLICATE KEY UPDATE item_id = '%s'"%(
            sucursal.database,
            sigla,
            date.today().strftime('%Y%m%d'),        
            sigla
        )
        print(sql)
        try:
            cursor.execute(sql)
            db.commit()
            print('ok')
        except Exception as err:
            print('error')
            print(err)
            db.rollback()
            return 'Error'

        db.close()
        return 'ok'

def centralizar_datos(suc):
    #instanciando las sucursales a las cuales se va a realizar la sustraccion de datos
    sucursal = models.Sucursal.objects.get(siglas = suc)
    sucursal2 = models.Sucursal.objects.get(siglas = suc)
    print('sucursal1')
    print(sucursal.ipaddress)
    print(sucursal.port)
    print(sucursal.usuario)
    print(sucursal.password)
    print(sucursal.database)
    print('sucursal 2')
    print(sucursal2.ipaddress)
    print(sucursal2.port)
    print(sucursal2.usuario)
    print(sucursal2.password)
    print(sucursal2.database)
    #lo que me interesa guardar es el kardex
    db = pymysql.connect(
        host=sucursal.ipaddress,
        port=int(sucursal.port),
        user=sucursal.usuario,
        passwd=sucursal.password,
        db=sucursal.database
    )
    db2 = pymysql.connect(
        host=sucursal2.ipaddress,
        port=int(sucursal2.port),
        user=sucursal2.usuario,
        passwd=sucursal2.password,
        db=sucursal2.database
    )
    cursor = db.cursor()
    cursor2 = db2.cursor()


    tomorrow = date.today()+ timedelta(days=1)
    tomorrow = tomorrow.strftime('%Y%m%d')
    hoy = date.today().strftime('%Y%m%d')

    sql = "select * from %s.inv_kardex where fecha between '%s' and '%s' and referencia != 'Apertura'"%(
        sucursal.database,
        hoy,
        tomorrow
    )

    print(sql)
    
    try:
        print('voy a selecccionar los registros del kardex de mi sucursal a la que le estoy jalando datos')
        cursor2.execute(sql)
        registros = cursor2.fetchall()
        print(registros)
        for registro in registros:
            ocodigo = registro[0]
            ofecha = registro[1]
            oreferencia = registro[2]
            oentrada = registro[3]
            osalida = registro[4]
            odebe = registro[5]
            ohaber = registro[6]
            osaldo = registro[7]
            ocostounitario = registro[8]
            oexistencia = registro[9]
            oitem_id = registro[10]
            osucursal_id = registro[11]
            k = models.Kardex.objects.create(
                fecha = ofecha,
                referencia = oreferencia,
                entrada = oentrada,
                salida = osalida,
                debe = odebe,
                haber = ohaber,
                saldo = osaldo,
                costounitario = ocostounitario,
                existencia = oexistencia,
                item = models.N4Item.objects.get(id_n4 = oitem_id),
                sucursal = models.Sucursal.objects.get(siglas = osucursal_id) 
            )
            print('inserte en mi kardex')
    
    except Exception as err:
        print('hubo algun error')
        print(err)
        db2.rollback()
        db2.close()
        return 'error'

    return 'ok'

def recalcular():
    print('recalculo')
    hoy = date.today()+ timedelta(days=1)
    hoy = hoy.strftime('%Y%m%d')
    # k = centralizar_datos('MA')
    # if k == 'ok': 
    #     print('centralize los datos')
    # else:
    #     print('no los centralize')
    sucursal = models.Sucursal.objects.get(siglas = 'DU')
    db = pymysql.connect(
        host=sucursal.ipaddress,
        port=int(sucursal.port),
        user=sucursal.usuario,
        passwd=sucursal.password,
        db=sucursal.database
    )
    cursor = db.cursor()

    sql = "call %s.recalculo('%s');"%(
        sucursal.database,
        hoy
    )
    print(sql)
    try:
        print('llame a mi recalculo')
        cursor.execute(sql)
        cursor.close()
        cursor = db.cursor()
        
        print('ejecutado')
        db.commit()
    except Exception as err:
        print('Error')
        print(err)
    
    # mayoreo = models.Sucursal.objects.get(siglas = 'MA')

    # dbMa = pymysql.connect(
    #     host=mayoreo.ipaddress,
    #     port=int(mayoreo.port),
    #     user=mayoreo.usuario,
    #     passwd=mayoreo.password,
    #     db=mayoreo.database
    # )
    # cursorMa = dbMa.cursor()


    # items = models.item_costo.objects.all()

    # for item in items:
    #     sql = "Update %s.inv_item_costo  set existencia = %s, costo = %s, saldo = %s where item_id = '%s'"%(
    #         mayoreo.database,
    #         item.existencia,
    #         item.costo,
    #         item.saldo,
    #         item.item.id_n4
    #     )
    #     print(sql)
    #     try:
    #         print('actualizando los costos en el mayoreo')
    #         cursorMa.execute(sql)
    #         print('costos actualizados')
    #         dbMa.commit()
    #     except Exception as err:
    #         print('error al actualizar los costos')
    #         print(err)
    #         dbMa.rollback()
    return 'ok'
