from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import pandas as pd

def gerar_pdf_localizacao(df, filename, agrupar=True, exibir_unitario=True, exibir_total=True):
    """
    Gera PDF do relatório de localização
    
    Args:
        df: DataFrame com os dados
        filename: Nome do arquivo a ser salvo
        agrupar: Se True, agrupa por prateleira
    """
    # Criar documento (margens mínimas no topo)
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           rightMargin=1*cm, leftMargin=1*cm,
                           topMargin=0.5*cm, bottomMargin=1*cm)
    
    # Container para elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo para título (ultra compacto)
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=10,
        textColor=colors.HexColor('#000080'),
        spaceAfter=1,
        spaceBefore=0,
        alignment=TA_CENTER
    )
    
    # Estilo para subtítulo (ultra compacto)
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=7,
        alignment=TA_CENTER,
        spaceAfter=4,
        spaceBefore=0
    )
    
    # Cabeçalho (ultra compacto - SEM espaço após data)
    elements.append(Paragraph("OFICINA AUTO PEÇAS", title_style))
    elements.append(Paragraph("POSIÇÃO DE ESTOQUE", title_style))
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", subtitle_style))
    # SEM Spacer - tabela começa direto!
    
    if agrupar:
        # Agrupar por prateleira (primeira letra/palavra da localização)
        df['GRUPO'] = df['PROD_LOCALIZACAOPECA'].apply(lambda x: str(x).split('-')[0] if pd.notna(x) else 'SEM LOC')
        
        total_geral = 0
        
        for grupo in sorted(df['GRUPO'].unique()):
            df_grupo = df[df['GRUPO'] == grupo]
            
            # SEM título de grupo - direto para a tabela
            # Cabeçalho dinâmico
            headers = ['Código', 'Descrição', 'Marca', 'Cód.Fab.', 'Local.', 'Estoque']
            if exibir_unitario: headers.append('Vl.Unit.')
            if exibir_total: headers.append('Vl.Total')
            data = [headers]
            
            subtotal = 0
            for idx, row in df_grupo.iterrows():
                codigo = str(row['PROD_CODIGO'])
                descricao = str(row['PROD_DESCRICAOPRODUTO'])[:40]  # Limitar tamanho
                marca = str(row.get('PROD_MARCA', '-') or '-')[:15]
                ref = str(row.get('PROD_CODIGOFABRICANTE', '-') or '-')[:15]
                local = str(row.get('PROD_LOCALIZACAOPECA', '-') or '-')
                estoque = row.get('PROD_QTDEESTOQUEFISICO', 0) or 0
                vl_unit = row.get('PROD_PRECOAVISTA', 0) or 0
                vl_total = row.get('VALOR_TOTAL', 0) or 0
                
                row_data = [
                    codigo,
                    descricao,
                    marca,
                    ref,
                    local,
                    str(int(estoque)) if estoque == int(estoque) else str(estoque).replace('.', ',')
                ]
                if exibir_unitario: row_data.append(f"{vl_unit:.2f}")
                if exibir_total: row_data.append(f"{vl_total:.2f}")
                
                data.append(row_data)
                subtotal += vl_total
            
            # Adicionar subtotal dinâmico
            if exibir_total:
                subtotal_row = ['', '', '', '', '', ''] # Fixo 6 colunas
                if exibir_unitario:
                    subtotal_row.append('Subtotal:')
                    subtotal_row.append(f"{subtotal:.2f}")
                else:
                    subtotal_row[-1] = 'Subtotal:'
                    subtotal_row.append(f"{subtotal:.2f}")
                data.append(subtotal_row)
            
            total_geral += subtotal
            
            # Recalcular larguras de colunas de forma estável (Total: 19cm)
            # Base para colunas fixas: Cod(1.2), Marca(2.8), Ref(1.5), Local(3.2), Estoque(1.8) = 10.5cm
            # Restante para Descrição + Preços = 8.5cm
            prices_width = (1.5 if exibir_unitario else 0) + (1.5 if exibir_total else 0)
            desc_width = 8.5 - prices_width
            
            col_widths = [1.2*cm, desc_width*cm, 2.8*cm, 1.5*cm, 3.2*cm, 1.8*cm]
            if exibir_unitario: col_widths.append(1.5*cm)
            if exibir_total: col_widths.append(1.5*cm)
            
            # Criar tabela
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (5, 1), (-1, -1), 'RIGHT'),  # Alinhar números à direita
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),  # Aumentado para 10pt
                ('FONTSIZE', (0, 1), (-1, -1), 6),  # Mantido 6pt para os dados
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 1.5),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),  # Subtotal
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.15*cm))
        
        # Total geral
        elements.append(Spacer(1, 0.5*cm))
        total_style = ParagraphStyle(
            'Total',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#000080'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(f"VALOR TOTAL: R$ {total_geral:.2f}", total_style))
    
    else:
        # Sem agrupamento - tabela única
        headers = ['Código', 'Descrição', 'Marca', 'Cód.Fab.', 'Local.', 'Estoque']
        if exibir_unitario: headers.append('Vl.Unit.')
        if exibir_total: headers.append('Vl.Total')
        data = [headers]
        
        total_geral = 0
        for idx, row in df.iterrows():
            codigo = str(row['PROD_CODIGO'])
            descricao = str(row['PROD_DESCRICAOPRODUTO'])[:40]
            marca = str(row.get('PROD_MARCA', '-') or '-')[:15]
            ref = str(row.get('PROD_CODIGOFABRICANTE', '-') or '-')[:15]
            local = str(row.get('PROD_LOCALIZACAOPECA', '-') or '-')
            estoque = row.get('PROD_QTDEESTOQUEFISICO', 0) or 0
            vl_unit = row.get('PROD_PRECOAVISTA', 0) or 0
            vl_total = row.get('VALOR_TOTAL', 0) or 0
            
            row_data = [
                codigo,
                descricao,
                marca,
                ref,
                local,
                str(int(estoque)) if estoque == int(estoque) else str(estoque).replace('.', ',')
            ]
            if exibir_unitario: row_data.append(f"{vl_unit:.2f}")
            if exibir_total: row_data.append(f"{vl_total:.2f}")
            
            data.append(row_data)
            total_geral += vl_total
        
        # Adicionar total dinâmico
        if exibir_total:
            total_row = ['', '', '', '', '', '']
            if exibir_unitario:
                total_row.append('Total:')
                total_row.append(f"{total_geral:.2f}")
            else:
                total_row[-1] = 'Total:'
                total_row.append(f"{total_geral:.2f}")
            data.append(total_row)
        
        # Recalcular larguras de colunas de forma estável (Total: 19cm)
        # Base para colunas fixas: Cod(1.2), Marca(2.8), Ref(1.5), Local(3.2), Estoque(1.8) = 10.5cm
        # Restante para Descrição + Preços = 8.5cm
        prices_width = (1.5 if exibir_unitario else 0) + (1.5 if exibir_total else 0)
        desc_width = 8.5 - prices_width
        
        col_widths = [1.2*cm, desc_width*cm, 2.8*cm, 1.5*cm, 3.2*cm, 1.8*cm]
        if exibir_unitario: col_widths.append(1.5*cm)
        if exibir_total: col_widths.append(1.5*cm)
        
        # Criar tabela
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (5, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),  # Aumentado para 10pt
            ('FONTSIZE', (0, 1), (-1, -1), 6),  # Mantido 6pt para os dados
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 1.5),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(table)
    
    # Gerar PDF
    doc.build(elements)
