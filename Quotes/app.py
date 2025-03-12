#Autor: Ryan Augusto Ribeiro
#Data de criação: 21/09/2024
#Data de modificação: 13/10/2024
#Modificação: Deixando o pdf responsivo, ou seja ao adicionar mais linhas ele vai se adequar
#para caber na pagina repartindo em mais folhas se necessario
# OBS: centralizado depois de mudar a grid

#importações
from flask import Flask, render_template, request, redirect, url_for #flask para usar html com python
from reportlab.pdfgen import canvas                                  #reportlab para gerar pdf
from reportlab.lib.pagesizes import A4                               #reportlab para gerar pdf (tamanho da pagina)
from reportlab.lib import colors                                     #reportlab para gerar pdf(cores)
from reportlab.lib.colors import HexColor                            #reportlab para gerar pdf(cores em hexa)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle,Paragraph                     #reportlab para gerar pdf(tabelas e estilo de tabelas)
from reportlab.pdfbase.ttfonts import TTFont                         #reportlab para gerar pdf(usar fontes externas)
from reportlab.pdfbase import pdfmetrics                             #reportlab para gerar pdf(usar fontes externas)
from datetime import datetime                                        #datetime para pegar a hora atual
import requests                                                      #usado para converter euro para real
import os
import sqlite3                                                       #banco de dados sql
from PyPDF2 import PdfReader, PdfWriter


# Registrar a fonte Arial
pdfmetrics.registerFont(TTFont('Arial', 'fonts/ariali.ttf'))
pdfmetrics.registerFont(TTFont('OpenSans', 'fonts/OpenSansRegular.ttf'))

#largura e altura da pagina 
page_width, page_height = A4


#inicializando app flask
app = Flask(__name__)

# CALCULAR A DATA ATUAL
data_atual = datetime.now().date().strftime("%d/%m/%Y")

# Mesclar dois pdfs
def merge_pdfs(pdf1, pdf2, output_filename):
    pdf_writer = PdfWriter()
    output_directory = os.path.join(os.path.expanduser("~"), "Desktop","BUDGETS")
    # Ler o primeiro PDF (gerado pelo ReportLab)
    with open(pdf1, 'rb') as f:
        pdf_reader1 = PdfReader(f)
        for page in pdf_reader1.pages:
            pdf_writer.add_page(page)

    # Ler o segundo PDF (o PDF existente)
    with open(pdf2, 'rb') as f:
        pdf_reader2 = PdfReader(f)
        for page in pdf_reader2.pages:
            pdf_writer.add_page(page)

   # Criar o diretório de saída se não existir
    os.makedirs(output_directory, exist_ok=True)

    # Caminho completo do PDF de saída
    output_path = os.path.join(output_directory, output_filename)

    # Escrever o PDF combinado
    with open(output_path, 'wb') as f:
        pdf_writer.write(f)


#iniciar banco de dados
def init_db():
    conn = sqlite3.connect('values.db')
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS valuesDublinM (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            euro REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS valuesDublinA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            euro REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS valuesCorkM (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            euro REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS valuesCorkA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            euro REAL NOT NULL
        );
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Formatar nome com "_"
def getname(nome_completo):
    partes = nome_completo.split()
    #primeiro_nome = partes[0]
    #sobrenome = partes[-1]
    #return primeiro_nome if primeiro_nome.lower() == sobrenome.lower() else primeiro_nome + sobrenome
    return "_".join(nome_completo.split())

# CONVERTE DE PONTO (INCH) PARA MM
def mm2p(milimetros):
    return milimetros / 0.35277

def p2mm(p):
    return p * 0.35277

#Função para formatar nome
def formatar_nome(nome):
    particulas = ['da', 'de', 'di', 'do', 'das', 'dos', 'van', 'von']
    partes = nome.split()

    # Formata cada parte do nome
    for i in range(len(partes)):
        if partes[i].lower() in particulas and i != 0 and i != len(partes) - 1:
            partes[i] = partes[i].lower()  # Mantém em minúscula se estiver no meio
        else:
            partes[i] = partes[i].title()  # Formata normalmente

    return ' '.join(partes)

linhas =[]
def adicionar():
    nova_linha = request.form.get('nova_linha')
    if nova_linha:
        linhas.append(nova_linha)
    return index()

# FUNÇÃO PRINCIPAL PARA GERAR O PDF DE ORÇAMENTO
def gerarpdf(nameNF, nationality, email, dataa, number):
    name = formatar_nome(nameNF)
    pdf_file = f"Quote_{getname(name)}.pdf"
    output_directory = os.path.join(os.path.expanduser("~"), "Desktop")
    pdf_path = os.path.join(output_directory, pdf_file)
    cnv = canvas.Canvas(pdf_path, pagesize=A4)
    cnv.setTitle(f"Quote_{getname(name)}")

    #iniciando sessao banco de dados
    conn = sqlite3.connect('values.db')
    cursor = conn.cursor()
    
   
    
    data_formatada = datetime.strptime(dataa, "%Y-%m-%d").strftime("%d/%m/%Y") # Formatando a data 

     # Criando estilo da primeira tabela
    espaco = mm2p(45)
   
    style = TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Alinha a primeira coluna à esquerda, exceto a última linha
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'), 
        #('ALIGN', (0, -1), (-1, -1), 'CENTER'),  # Alinha a última linha ao centro 
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (-1, 0), (-1, -1), 'CENTER'),  # Alinha a última coluna à direita
        ('FONTNAME', (0, 0), (-1, -1), 'OpenSans'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7), 
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.black),
        #('BOX', (0, 0), (-1, -1), 0.5, colors.black)  
    ])
    style2 = TableStyle([
                    
                ]) 

    

    # Criando estilo da segunda tabela
    styleTB = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'OpenSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
        #('BOX', (0, 0), (-1, -1), 0.5, colors.black)
    ])

    

    #mudando a cor de fundo
    
    def InitPage():
        cnv.setFillColor(colors.HexColor("#55cc6f"))  # Cor de fundo em hexadecimal
        cnv.setFillAlpha(0.25)
        cnv.rect(0, 0, page_width, page_height, fill=True, stroke=False)  # Desenha um retângulo
        cnv.setFillColor(colors.black)

        #Define a opacidade (entre 0.0 e 1.0)
        cnv.setFillAlpha(0.37)  # 90% de opacidade 
        cnv.drawImage("static/wave.png", mm2p(0), mm2p(255), width=mm2p(251.4), height=mm2p(47),mask='auto')
        cnv.drawImage("static/waveB.png", mm2p(0), mm2p(-5), width=mm2p(251.4), height=mm2p(50),mask='auto')
        cnv.setFillAlpha(1) 

        # Desenhando a imagem no fundo do pdf
        cnv.setFillAlpha(0.15)
        cnv.drawImage("static/logov2.png",((A4[0]-mm2p(200))/2)+ mm2p(50),(A4[1]-mm2p(200))/2, width=mm2p(200),height=mm2p(200),preserveAspectRatio = 'true' ,mask='auto')
        cnv.setFillAlpha(1)
    
    InitPage()
    
    # Logo da Erin
    cnv.drawImage("static/logo.png", mm2p(5), mm2p(255), width=251.4, height=60,mask='auto')

    # Linha de marcação de cabeçalho
    cnv.setStrokeColor("#014108")
    cnv.line(mm2p(0), mm2p(250), mm2p(210), mm2p(250))

    # Dados da tabela
    data = [
        ["DESCRIPTION", "PRICE (€)"]       
    ]
    

    selected_city = request.form.get('city')
    selected_period = request.form.get('period')


    if selected_city == 'dublin' and selected_period == 'morning' :
        cursor.execute("SELECT euro FROM valuesDublinM")
        result = cursor.fetchall()
    elif selected_city == 'dublin' and selected_period == 'afternoon':
        cursor.execute("SELECT euro FROM valuesDublinA")
        result = cursor.fetchall()
    elif selected_city == 'cork' and selected_period == 'morning':
        cursor.execute("SELECT euro FROM valuesCorkM")
        result = cursor.fetchall()
    elif selected_city == 'cork' and selected_period == 'afternoon':
        cursor.execute("SELECT euro FROM valuesCorkA")
        result = cursor.fetchall()

    # Verifica se há values retornados
    if len(result) >= 5:
        vlr_engcourse = result[0][0]  # Primeiro valor
        vlr_medins = result[1][0]     # Segundo valor
        vlr_leranins = result[2][0]   # Terceiro valor
        vlr_txtbook = result[3][0]    # Quarto valor
        vlr_exam = result[4][0]       # Quinto valor
    else:
        # Se não houver values suficientes, pode definir values padrão ou lidar com o erro
        vlr_engcourse, vlr_medins, vlr_leranins, vlr_txtbook, vlr_exam = 0, 0, 0, 0, 0

    if request.method == "POST":
        depositado = float(request.form["dep"])
        agente = request.form["agent"]

        engcourse = 'engcourse' in request.form
        medins = 'medins' in request.form
        leranins = 'leranins' in request.form
        txtbook = 'txtbook' in request.form
        exam = 'exam' in request.form

    #Fazendo append na tabela dados caso esteja selecionado no forms
    if engcourse:
        data.append(["25-week course General English/15h", f"€ {vlr_engcourse:.2f}"])
    if medins:
        data.append(["Medical insurance", f"€ {vlr_medins:.2f}"])
    if leranins:
        data.append(["Learner protection", f"€ {vlr_leranins:.2f}"])
    if txtbook:
        data.append(["Textbook", f"€ {vlr_txtbook:.2f}"])
    if exam:
        data.append(["Exam", f"€ {vlr_exam:.2f}"])

    #dando append na tabela dados das linhas novas
    for i in range(0, len(request.form.getlist('description'))):
            descricao = request.form.getlist('description')[i]
            valor_euro = float(request.form.getlist('value_euro')[i])
            data.append([descricao, f"€ {valor_euro:.2f}"])

    # Calcular o total da tabela
    total_euro =sum(float(row[1].replace("€", "").replace(",", ".")) for row in data[1:]) # Somar a coluna EURO

    # Adicionar o total na tabela
    data.append([ "TOTAL",f"€ {total_euro:,.2f}"])
        
    numero_de_linhas = len(data)
    print(f"Num de linhas:  {numero_de_linhas}")
    FSF = 14
    match numero_de_linhas:
            case n if n > 7 and n < 10: # 1 a 2 linhas a mais
                espaco = espaco - ( (n-7) *(mm2p(54.33)/7)  )
                print(f"o valor de nc1 é : {n}")
                print(f"o espaço é: {p2mm(espaco)}")
                AY,RY = 0,0
            
                


            case n if n == 10 : # 3 linhas a mais
                espaco = espaco - ( 2 *(mm2p(54.33)/7)  )
                print(f"o valor de nc1 é : {n}")
                print(f"o espaço é: {p2mm(espaco)}")
                AY = mm2p(5)
                RY = (((2) *(mm2p(54.33)/7)) - AY)*(40/100)
                AE = ((n-7) *(mm2p(54.33)/7))/ ((2) *(mm2p(54.33)/7)) #A/DE crescimo de espaço
              

                style2 = TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), FSF),
                ])
            
            case n if n > 10: #mais de 5 linhas a mais
                espaco = espaco - ( 2 *(mm2p(54.33)/7)  )
                print(f"o valor de nc1 é : {n}")
                print(f"o espaço é: {p2mm(espaco)}")
                AY = mm2p(0)
                RY = 0
                AE = ((n-7) *(mm2p(54.33)/7))/ ((2) *(mm2p(54.33)/7)) #A/DE crescimo de espaço
              

                style2 = TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), FSF),
                ])

            case n_:
                espaco = espaco
                print(f"o valor de ncd é :{n}")
                AY,RY = 0,0
            

    print(f"o tamanho da fonte é: {FSF}\n")
    
    
     

    #dados bank da empresa em dublin
    dublin = [
        ["Bank Name","DUBLIN Bank Name"],
        ["IBAN","DUBLIN IBAN"],
        ["Account Name","Account Name"],
        ["Swift code","Swift code"],
        ["Account number","Account number"],
        ["Branch sort code ","Branch sort code "],
        ["Bank address","Bank address"]
    ]

    #dados bank da empresa em cork
    cork = [
        ["Bank Name"," CORK Bank Name"],
        ["IBAN","CORK IBAN"],
        ["Account Name","Account Name"],
        ["Swift code","Swift code"],
        ["Account number","Account number"],
        ["Branch sort code ","Branch sort code "],
        ["Bank address","Bank address"]
    ]
   


   

    # Configurar a primeira tabela
    maior_elemento = pdfmetrics.stringWidth(max(data, key=lambda x: len(x[0]))[0], 'OpenSans', 14)
    colwidth = [260,mm2p(60)] if maior_elemento <= 252 else  [None,mm2p(60)]
    table = Table(data,colWidths=colwidth)
    table.setStyle(style)                           # Colocando estilo na primeira tabela
    table.setStyle(style2)
    table_width, table_height = table.wrap(0, 0)    # Calcular a largura da primeira tabela e a posição X para centralização

    # Configurando a segunda tabela com base na opção escolhida da cidade
    if selected_city == 'dublin':
        tableBank = Table(dublin, colWidths = table_width / 2 )
    else:
        tableBank = Table(cork, colWidths = table_width / 2)

    # Configurando a segunda tabela
    tableBank.setStyle(styleTB)# Adicionando estilo a segunda tabela
    tableBank.setStyle(style2)
    tableB_width, tableB_height = tableBank.wrap(0, 0)  # Pegando a medida da largura e altura da segunda tabela

    


    x_positionT = (A4[0] - table_width) / 2             # Centraliza a primeira tabela na largura da página
    if numero_de_linhas > 10:
        y_positionT = ( (page_height-mm2p(47)) /2) - (table_height/2)
        y_quote = y_positionT + table_height + mm2p(20)

    else:
        y_positionT = (mm2p(250) -mm2p(25) - table_height + AY ) # Centraliza a primeira tabela na largura da página
        y_quote = mm2p(240)
    
    #Cotação cidade e periodo 
    cnv.setFont("Helvetica-Bold", 16)
    cnv.drawCentredString(page_width/2, y_quote, f"Quote {formatar_nome(selected_city)} {formatar_nome(selected_period)}")
    cnv.setFont("OpenSans", FSF)

    y_TB = y_positionT -tableB_height - espaco        # Calculando o Y da segunda tabela

    #Circulos na posição das tabelas para melhor visualização
    # cnv.circle(x_positionT,y_positionT,2)
    # cnv.circle(x_positionT,y_TB,2)
    # print(f"TB_height: {p2mm(table_height)} mm")  #print apenas para teste 
    

      
   
 
    # Adicionando primeira tabela ao canvas
    table.wrapOn(cnv, 0, 0)
    table.drawOn(cnv, x_positionT,y_positionT)

    

    #Escrevendo as strings, titulos e etc

    # Dados do aluno
    cnv.setFont("OpenSans", FSF)  #setando a fonte como OpenSans
    cnv.drawString(mm2p(105), mm2p(280), f"Full name:                {name}")
    cnv.drawString(mm2p(105), mm2p(275), f"Nationality:              {formatar_nome(nationality)}")
    cnv.drawString(mm2p(105), mm2p(270), f"Email:                        {email}")
    cnv.drawString(mm2p(105), mm2p(265), f"Course start date:  {data_formatada}")
    cnv.drawString(mm2p(105), mm2p(260), f"Contact number:    {number}")


    cnv.drawString(x_positionT,y_positionT + mm2p(2) + table_height, "Package details:")
    cnv.drawString(x_positionT,y_positionT - mm2p(6), f"Deposit:    € {depositado:,.2f} Paid")
    cnv.drawString(x_positionT,y_positionT - mm2p(12), f"Financial:  € {total_euro - depositado:,.2f} ")


   
    if numero_de_linhas >10 :
        cnv.showPage()
        InitPage()
        y_TB =  ((page_height/2) + mm2p(20) - (tableB_height/2) + AY )
    

    cnv.setFontSize(FSF)
    # Adicionando segunda tabela ao canvas
    tableBank.wrapOn(cnv, 0, 0)
    tableBank.drawOn(cnv,x_positionT,y_TB)
    cnv.drawString(x_positionT,y_TB + tableB_height + mm2p(2), "BANK ACCOUNT DETAILS:")
    cnv.drawCentredString(page_width/2,y_TB - mm2p(10) , "When you send your payment, please write your name in the description.")
    cnv.drawCentredString(page_width/2,y_TB - mm2p(20) , "THANK YOU!")
    cnv.drawImage("static/assig.png", (page_width/2)-mm2p(13),mm2p(25), width=mm2p(30), height=mm2p(30),mask='auto') 
    
    
    # Rodapé
    cnv.line(mm2p(0), mm2p(29), mm2p(210), mm2p(29))  # Linha 
    cnv.drawString(mm2p(5), mm2p(37), f"Agent: {formatar_nome(agente)}")
    cnv.drawString(mm2p(5), mm2p(31), f"Date: {data_atual}")
    cnv.drawImage("static/selos.png",0,-mm2p(8),width=page_width,preserveAspectRatio = 'true')
 

    # Salvar o PDF
    cnv.save()
    merge_pdfs("static/Erin.pdf",pdf_path,pdf_file)

    print(f"Gerado arquivo {pdf_file}")
    print(f"A primeira coluna tem largura: {table._colWidths[0]} inch ou {p2mm(table._colWidths[0])} mm")
    print(f"Medida do texto bank:  {pdfmetrics.stringWidth("IE65 AIBK 93 11 01 6834 6000", 'OpenSans', 14)}")
    print(f"Medida do texto curso:  {pdfmetrics.stringWidth("25-week course General English/15h ", 'OpenSans', 14)}")
    print(f"Maior elemto: {maior_elemento}")


    print(f" 251 mm = {mm2p(251.4)}")
    print(f" page height= {page_height}") 
    print(f" page height= {p2mm(page_height)} mm") 


@app.route("/", methods=["GET", "POST"]) 
def index():
    if request.method == "POST":
        name = request.form["name"]
        nationality = request.form["nationality"]
        email = request.form["email"]
        date = request.form["date"]
        number = request.form["number"]

        gerarpdf(name, nationality, email, date, number)
        return redirect(url_for("index"))

    return render_template("form.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    conn = sqlite3.connect('values.db', timeout=10)
    cursor = conn.cursor()

    if request.method == "POST":
        tabela = request.form["tabela"]
        novos_values = request.form.getlist("values")

        try:
            cursor.execute(f"DELETE FROM {tabela}")
            cursor.executemany(f"INSERT INTO {tabela} (descricao, euro) VALUES (?, ?)", [
                ("25-week course General English/15h", float(novos_values[0])) if novos_values[0] else (None, 0),
                ("Medical insurance", float(novos_values[1])) if novos_values[1] else (None, 0),
                ("Learner protection insurance", float(novos_values[2])) if novos_values[2] else (None, 0),
                ("Textbook", float(novos_values[3])) if novos_values[3] else (None, 0),
                ("EXAM", float(novos_values[4])) if novos_values[4] else (None, 0)
            ])
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("Erro ao atualizar a tabela:", e)
        finally:
            conn.close()
        return redirect(url_for("edit"))

    tabela_selecionada = request.args.get("tabela", "valuesDublinM") or request.form.get("tabela", "valuesDublinM")
    cursor.execute(f"SELECT euro FROM {tabela_selecionada}")
    values = cursor.fetchall()
    values = [valor[0] for valor in values]

    conn.close()
    return render_template("edit.html", values=values, tabela=tabela_selecionada)


if __name__ == "__main__":
    app.run(debug=True)
