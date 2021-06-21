from . import models

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseNotFound

from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def pdf_view(request):
    fs = FileSystemStorage() 
    filename = 'inv/CVRoy.pdf'
    print(fs.location)
    print(fs.exists(filename))
    if fs.exists(filename):
        with fs.open(filename) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="inv/CVRoy.pdf"'
            return response
    else:
        return HttpResponseNotFound('No se encontro archivo PDF')

def write_pdf_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['content-Disposition'] = 'inline;filename="mypdf.pdf"'

    #Asignamos un buffer de memoria y en el lienzo le decimos que sea sobre el buffer
    buffer = BytesIO()
    lienzo = canvas.Canvas(buffer,pagesize=A4)
    w,h = A4
    
    #comenzamos a escribir el pdf aqui
    lienzo.setFont("Helvetica",25)
    lienzo.drawString(50,h-50,'Hola señor Bell.')
    lienzo.showPage()
    #End Writing

    text = lienzo.beginText(50,h-70)
    text.setFont("Helvetica",12)
    text.textLine("Esto es un prueba de report lab")
    text.textLine("para ver como funciona")
    lienzo.drawText(text)
    lienzo.showPage()

    # lienzo.drawImage("inv/FENICOOTAXI.png", 50, h - 50)
    

    lienzo.save()
    
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


# PARA ESCRIBRIR UN PDF EN UNA RUTA ESPECIFICA DEL SERVIDOR
# def write_pdf_view(request):
#     doc = SimpleDocTemplate("D:/Documento/Reporte.pdf")
#     styles = getSampleStyleSheet()
#     Story = [Spacer(1,2*inch)]
#     style = styles["Normal"]

#     for i in range(100):
#        bogustext = ("El ojo Quiebro %s.  " % i) * 20
#        p = Paragraph(bogustext, style)
#        Story.append(p)
#        Story.append(Spacer(1,0.2*inch))
#     doc.build(Story)

#     fs = FileSystemStorage("D:/Documento/")
#     with fs.open("Reporte.pdf") as pdf:
#         response = HttpResponse(pdf, content_type='application/pdf')
#         # response['Content-Disposition'] = 'attachment; filename="Reporte.pdf"'
#         response['Content-Disposition'] = 'inline; filename="Reporte.pdf"'
#         return response

#     return response



def generar_pdf(request):
    # print ("Genero el PDF")
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "clientes.pdf"  # llamado clientes
    # la linea 26 es por si deseas descargar el pdf a tu computadora
    # response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )
    clientes = []
    styles = getSampleStyleSheet()
    header = Paragraph("Listado de Items", styles['Heading1'])
    clientes.append(header)
    headings = ('Bodega', 'Item', 'Cantidad', 'Costo')
    allclientes = [(p.bodega, p.item, p.cantidad, p.costo) for p in models.AjusteDet.objects.all()]
    # print(allclientes)

    t = Table([headings] + allclientes)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (3, -1), 1, colors.dodgerblue),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)
        ]
    ))
    clientes.append(t)
    doc.build(clientes)
    response.write(buff.getvalue())
    buff.close()
    return response