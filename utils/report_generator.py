# utils/report_generator.py
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from datetime import datetime
import os

class ReportGenerator:
    def __init__(self):
        self.header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        self.header_font = Font(color="FFFFFF", bold=True)
        self.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
    def generate_excel_report(self, analysis_results, output_path="reports"):
        """
        Gera relatório Excel com análise de sazonalidade
        
        Args:
            analysis_results: Dicionário com resultados da análise
            output_path: Caminho para salvar o relatório
            
        Returns:
            str: Caminho do arquivo gerado
        """
        # Criar diretório se não existir
        os.makedirs(output_path, exist_ok=True)
        
        # Criar workbook
        wb = Workbook()
        
        # Aba de Resumo
        ws = wb.active
        ws.title = "Resumo"
        
        # Título
        ws['A1'] = "ANÁLISE DE SAZONALIDADE"
        ws['A1'].font = Font(size=16, bold=True)
        ws.merge_cells('A1:D1')
        
        # Informações gerais
        ws['A3'] = "Período Analisado:"
        ws['B3'] = f"{analysis_results.get('period', {}).get('start', 'N/A')} a {analysis_results.get('period', {}).get('end', 'N/A')}"
        
        ws['A4'] = "Total de SKUs:"
        ws['B4'] = analysis_results.get('total_skus', 0)
        
        ws['A5'] = "SKUs Sazonais:"
        ws['B5'] = analysis_results.get('seasonal_skus', 0)
        
        ws['A6'] = "% de Sazonalidade:"
        ws['B6'] = f"{analysis_results.get('seasonality_percentage', 0):.2f}%"
        
        # Estatísticas principais
        ws['A8'] = "ESTATÍSTICAS"
        ws['A8'].font = Font(bold=True)
        
        stats = analysis_results.get('stats', {})
        
        ws['A9'] = "Média:"
        ws['B9'] = f"{stats.get('mean', 0):.2f}"
        
        ws['A10'] = "Desvio Padrão:"
        ws['B10'] = f"{stats.get('std', 0):.2f}"
        
        ws['A11'] = "Coeficiente de Variação:"
        ws['B11'] = f"{stats.get('cv', 0):.2f}%"
        
        ws['A12'] = "Mínimo:"
        ws['B12'] = f"{stats.get('min', 0):.2f}"
        
        ws['A13'] = "Máximo:"
        ws['B13'] = f"{stats.get('max', 0):.2f}"
        
        # Adicionar aba de SKUs se houver dados
        if 'sku_metrics' in analysis_results and analysis_results['sku_metrics']:
            ws2 = wb.create_sheet("SKUs")
            
            # Cabeçalhos
            headers = ['SKU', 'Descrição', 'Categoria', 'Sazonal', 'Índice (%)', 'CV (%)', 'Vendas Média']
            for col, header in enumerate(headers, 1):
                cell = ws2.cell(row=1, column=col, value=header)
                cell.fill = self.header_fill
                cell.font = self.header_font
                cell.border = self.border
            
            # Dados
            for row, item in enumerate(analysis_results['sku_metrics'], 2):
                ws2.cell(row=row, column=1, value=item.get('sku', '')).border = self.border
                ws2.cell(row=row, column=2, value=item.get('description', '')).border = self.border
                ws2.cell(row=row, column=3, value=item.get('category', '')).border = self.border
                ws2.cell(row=row, column=4, value='Sim' if item.get('is_seasonal', False) else 'Não').border = self.border
                ws2.cell(row=row, column=5, value=f"{item.get('seasonality_index', 0):.2f}").border = self.border
                ws2.cell(row=row, column=6, value=f"{item.get('cv', 0):.2f}").border = self.border
                ws2.cell(row=row, column=7, value=f"{item.get('avg_sales', 0):.2f}").border = self.border
        
        # Salvar arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analise_sazonalidade_{timestamp}.xlsx"
        filepath = os.path.join(output_path, filename)
        
        wb.save(filepath)
        return filepath
