from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

class KardexPDFGenerator:
    def __init__(self):
        self.pagesize = A4  # Retrato
        self.width, self.height = self.pagesize
        
    def gerar_pdf(self, filename, dados, produto_codigo, produto_descricao, 
                  data_ini, data_fim, totalizadores):
        """
        Gera PDF do Kardex
        
        Args:
            filename: Nome do arquivo PDF
            dados: DataFrame com as movimentações
            produto_codigo: Código do produto
            produto_descricao: Descrição do produto
            data_ini: Data inicial do período
            data_fim: Data final do período
            totalizadores: Dict com entradas, saidas, devolucoes, saldo
        """
        doc = SimpleDocTemplate(
            filename,
            pagesize=self.pagesize,
            rightMargin=3*mm,
            leftMargin=3*mm,
            topMargin=10*mm,
            bottomMargin=10*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Estilo para cabeçalho
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=8,
            alignment=0,  # Left
        )
        
        center_style = ParagraphStyle(
            'CustomCenter',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,  # Center
            fontName='Helvetica-Bold'
        )
        
        right_style = ParagraphStyle(
            'CustomRight',
            parent=styles['Normal'],
            fontSize=8,
            alignment=2,  # Right
        )
        
        # === CABEÇALHO ===
        # Linha 1: Empresa | Título | Página e Período
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data_ini_str = data_ini.strftime("%d/%m/%Y")
        data_fim_str = data_fim.strftime("%d/%m/%Y")
        
        header_data = [
            [
                Paragraph("ORIGINAL AUTO PEÇAS", header_style),
                Paragraph("<b>EXTRATO DO PRODUTO</b>", center_style),
                Paragraph(f"Pag. 001<br/>Período: {data_ini_str}  {data_fim_str}", right_style)
            ]
        ]
        
        header_table = Table(header_data, colWidths=[60*mm, 70*mm, 60*mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 3*mm))
        
        # Data de geração
        story.append(Paragraph(f"Data: {data_atual}", header_style))
        story.append(Spacer(1, 3*mm))
        
        # Informações do produto
        produto_info = f"PRODUTO:  {produto_codigo}  {produto_descricao}"
        story.append(Paragraph(produto_info, header_style))
        story.append(Spacer(1, 3*mm))
        
        # Linha separadora
        line_data = [['_' * 150]]
        line_table = Table(line_data, colWidths=[190*mm])
        story.append(line_table)
        story.append(Spacer(1, 2*mm))
        
        # === CABEÇALHO DA TABELA ===
        table_data = [[
            'DATA', 'CODIGO', 'DESCRICAO', 'TIPO', 'NUM NF', 
            'PEDIDO', 'QTDE', 'VR UNIT', 'VR TOTAL'
        ]]
        
        
        # === DADOS ===
        for _, row in dados.iterrows():
            data = row['DATA'].strftime('%d/%m/%Y') if hasattr(row['DATA'], 'strftime') else row['DATA']
            codigo = str(row['COD_ENTIDADE']) if row['COD_ENTIDADE'] else ''
            descricao = str(row['NOME_ENTIDADE']) if row['NOME_ENTIDADE'] else ''
            # TIPO mostra ENTRADA (EE) ou SAIDA (VI)
            tipo = str(row['TIPO']) if row['TIPO'] else ''
            num_nota = str(row['NUM_NOTA']) if row['NUM_NOTA'] else ''
            pedido = str(row['PEDIDO']) if row['PEDIDO'] else ''
            qtde = str(int(row['QTDE'])) if row['QTDE'] else '0'
            valor_unit = f"{row['VALOR_UNIT']:.2f}".replace('.', ',') if row['VALOR_UNIT'] else '0,00'
            valor_total = f"{row['TOTAL']:.2f}".replace('.', ',') if row['TOTAL'] else '0,00'
            
            table_data.append([
                data, codigo, descricao, tipo, num_nota, 
                pedido, qtde, valor_unit, valor_total
            ])
        
        # Linha separadora antes dos totais
        table_data.append(['_' * 10] * 9)
        
        # === TOTALIZADORES ===
        estoque_anterior = totalizadores.get('estoque_anterior', 0)
        entradas = totalizadores.get('entradas', 0)
        saidas = totalizadores.get('saidas', 0)
        devolucoes = totalizadores.get('devolucoes', 0)
        saldo = totalizadores.get('saldo', 0)
        
        totais_text = f"ESTOQUE ANTERIOR=>  {int(estoque_anterior)}        ENTRADA=>      {int(entradas)}        SAIDA=>      {int(saidas)}        DEVOLUCAO=>      {int(devolucoes)}                SALDO DO ESTOQUE==>      {int(saldo)}"
        table_data.append([totais_text, '', '', '', '', '', '', '', ''])
        
        # Linha separadora final
        table_data.append(['_' * 10] * 9)
        
        # === CRIAR TABELA ===
        # Larguras ajustadas para RETRATO (sem VEND): Data, Codigo, Descricao, Tipo, Num NF, Pedido, Qtde, Vr Unit, Vr Total
        col_widths = [20*mm, 12*mm, 64*mm, 22*mm, 18*mm, 16*mm, 11*mm, 20*mm, 20*mm]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo da tabela
        table_style = [
            # Cabeçalho
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            
            # Dados - fonte reduzida para 6.5
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 6.5),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # Padrão: esquerda
            ('ALIGN', (6, 1), (6, -1), 'CENTER'),  # Qtde centralizada
            ('ALIGN', (7, 1), (7, -1), 'LEFT'),    # Vr Unit à esquerda
            ('ALIGN', (8, 1), (8, -1), 'LEFT'),    # Vr Total à esquerda
            
            # Bordas - padding reduzido
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]
        
        table.setStyle(TableStyle(table_style))
        story.append(table)
        
        # Gerar PDF
        doc.build(story)
        
        return filename
