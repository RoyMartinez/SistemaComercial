import time, os
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch,cm, mm
from vta.models import Facturamsr, Facturadet
from django.conf import settings
from django.db.models import Sum, F, FloatField, ExpressionWrapper

def auto_facturar(fact): 
    f = Facturamsr.objects.get(pk=fact)
    archivo = str(fact) + '.pdf'
    x = os.path.join(settings.MEDIA_ROOT, archivo)
    doc = SimpleDocTemplate(x, pagesize=(76*mm, 200*mm), rightMargin=0, leftMargin=0, topMargin=3, bottomMargin=3)
    Story=[]
    
    address_parts = ["RUC J0810000002960 - Tel 22631512", "AUT-DGI: ASFC-04-0126-09-2013-2",str(f.fechaemision),"Fact " + str(f.serie) + " - Venta de " + str(f.formapago.condicion), "Cliente: "+ str(f.cliente),str(f.nombre)] 
        
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, ))
    ptext = '<font size=12>{}</font>'.format('FENICOOTAXI, R.L.')
    
    Story.append(Paragraph(ptext, styles["Center"]))
    Story.append(Spacer(1, 12))

    ptext = '<font size=10>{}</font>'.format('SUCURSAL '+ str(f.sucursal).upper())
    Story.append(Paragraph(ptext, styles["Center"]))
    Story.append(Spacer(1, 12))

    ptext = '<font size=9>{}</font>'.format(str(f.sucursal.direccion))
    Story.append(Paragraph(ptext, styles["Center"]))       
    for part in address_parts:
        ptext = '<font size=9>%s</font>' % part.strip()
        Story.append(Paragraph(ptext, styles["Center"]))   
    Story.append(Spacer(1, 12))
    Story.append(Spacer(1, 12))

    styleN = styles["BodyText"]
    styleN.alignment = TA_LEFT
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER

    # Headers
    hbod = Paragraph('<font size=8>Bod</font>', styleBH)
    hcant = Paragraph('<font size=8>Cant</font>', styleBH)
    hdec = Paragraph('<font size=8>Descripcion</font>', styleBH)
    hprecio = Paragraph('<font size=8>Precio</font>', styleBH)

    data= [['----------------------------------------------------------'],
            [hbod, hcant, hdec, hprecio],
            ['----------------------------------------------------------'],
    ]
    #detalle = Facturadet.objects.filter(referencia = fact)
    detalle = Facturadet.objects.filter(referencia=fact).annotate(factor=ExpressionWrapper(F('unidades')*F('item__precio'), output_field=FloatField()))
    for i in detalle:
        bod = Paragraph('<font size=8>' + str(i.bodega.pk).lower() + '</font>', styleN)
        desc = Paragraph('<font size=8>' + str(i.item.descripcion).lower() + '</font>', styleN)
        cantidad = Paragraph('<font size=8>'+ str(i.unidades) + '</font>', styleBH)
        precio = Paragraph('<font size=8>' + str(round(float(i.factor),2)) + '</font>', styleN)
        data.append([bod, cantidad, desc, precio])
    data.append(['   ----------------------------------------------------------'])
    subtotal = Facturadet.objects.filter(referencia=fact).aggregate(suma=Sum(F('unidades')*F('item__precio'), output_field=FloatField()))
    data.append(['',Paragraph('<font size=8>Subtotal: </font>', styleN), Paragraph('<font size=8>'+ str(round(subtotal['suma'],2)) +'</font>', styleN)])
    data.append(['',Paragraph('<font size=8>Descuento: </font>', styleN), Paragraph('<font size=8>'+ str(round(f.descuentotal,2)) +'</font>', styleN)])
    data.append(['',Paragraph('<font size=8>Impuesto: </font>', styleN), Paragraph('<font size=8>'+ str(round(f.impuestototal,2)) +'</font>', styleN)])
    data.append(['',Paragraph('<font size=8>Total: </font>', styleN), Paragraph('<font size=8>'+ str(round(f.preciofinaltotal,2)) +'</font>', styleN)])

    table = Table(data, colWidths=[1.1 * cm, 3 * cm, 2 * cm])
    Story.append(table)
    Story.append(Spacer(1, 12))
    Story.append(Spacer(1, 12))

    ptext = '<font size=10>{}</font>'.format('Le atendio ' + str(f.vendedor.identificacion.first_name) + ' ' + str(f.vendedor.identificacion.last_name))
    Story.append(Paragraph(ptext, styles["Center"]))

    Story.append(Spacer(1, 12))
    Story.append(Spacer(1, 12))

    doc.build(Story)
    #cmd = 'lp ' + x
    #os.system(cmd)