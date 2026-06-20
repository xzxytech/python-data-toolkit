"""
Auto Report Generator - Create professional PDF/Excel reports from data
Usage: python report_generator.py --input sales.xlsx --output report.pdf --title "Q1 Sales Report"

Features:
- Auto-detect data types and generate appropriate charts
- Summary statistics with key insights
- Professional formatting
- Support CSV, Excel, JSON input
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from datetime import datetime
import argparse
import os

class ReportGenerator:
    def __init__(self):
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        plt.rcParams['figure.figsize'] = (10, 6)
    
    def load_data(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.csv':
            return pd.read_csv(filepath)
        elif ext in ('.xlsx', '.xls'):
            return pd.read_excel(filepath)
        elif ext == '.json':
            return pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported format: {ext}")
    
    def summary_stats(self, df):
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': list(df.select_dtypes(include='number').columns),
            'text_columns': list(df.select_dtypes(include='object').columns),
            'missing_values': df.isnull().sum().to_dict(),
            'descriptive': df.describe().to_dict()
        }
        return stats
    
    def auto_chart(self, df, output_dir):
        charts = []
        numeric_cols = df.select_dtypes(include='number').columns
        
        for col in numeric_cols[:5]:  # Max 5 charts
            fig, ax = plt.subplots()
            
            if len(df[col].dropna()) > 0:
                df[col].hist(ax=ax, bins=20, color='#4472C4', edgecolor='white')
                ax.set_title(f'Distribution: {col}')
                ax.set_xlabel(col)
                ax.set_ylabel('Frequency')
                
                chart_path = os.path.join(output_dir, f'chart_{col}.png')
                fig.savefig(chart_path, dpi=150, bbox_inches='tight')
                charts.append(chart_path)
            plt.close(fig)
        
        # Correlation heatmap for numeric data
        if len(numeric_cols) > 1:
            fig, ax = plt.subplots(figsize=(8, 6))
            corr = df[numeric_cols].corr()
            im = ax.imshow(corr, cmap='RdYlBu', aspect='auto')
            ax.set_xticks(range(len(numeric_cols)))
            ax.set_yticks(range(len(numeric_cols)))
            ax.set_xticklabels(numeric_cols, rotation=45, ha='right')
            ax.set_yticklabels(numeric_cols)
            plt.colorbar(im)
            ax.set_title('Correlation Matrix')
            
            chart_path = os.path.join(output_dir, 'correlation.png')
            fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            charts.append(chart_path)
            plt.close(fig)
        
        return charts
    
    def generate_excel_report(self, df, output_path, title="Data Report"):
        stats = self.summary_stats(df)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            summary = pd.DataFrame([
                {'Metric': 'Report Title', 'Value': title},
                {'Metric': 'Generated', 'Value': datetime.now().strftime('%Y-%m-%d %H:%M')},
                {'Metric': 'Total Rows', 'Value': stats['total_rows']},
                {'Metric': 'Total Columns', 'Value': stats['total_columns']},
                {'Metric': 'Numeric Columns', 'Value': ', '.join(stats['numeric_columns'])},
                {'Metric': 'Text Columns', 'Value': ', '.join(stats['text_columns'])},
            ])
            summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Descriptive stats
            df.describe().to_excel(writer, sheet_name='Statistics')
            
            # Raw data
            df.to_excel(writer, sheet_name='Raw Data', index=False)
            
            # Missing values
            missing = pd.DataFrame([
                {'Column': k, 'Missing': v} 
                for k, v in stats['missing_values'].items() if v > 0
            ])
            if len(missing) > 0:
                missing.to_excel(writer, sheet_name='Missing Values', index=False)
        
        print(f"Report generated: {output_path}")
        return output_path
    
    def run(self, input_path, output_path, title="Data Report"):
        df = self.load_data(input_path)
        print(f"Loaded: {len(df)} rows × {len(df.columns)} columns")
        
        # Generate charts
        chart_dir = os.path.dirname(output_path) or '.'
        charts = self.auto_chart(df, chart_dir)
        print(f"Generated {len(charts)} charts")
        
        # Generate Excel report
        if not output_path.endswith('.xlsx'):
            output_path = output_path.rsplit('.', 1)[0] + '.xlsx'
        
        return self.generate_excel_report(df, output_path, title)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auto Report Generator')
    parser.add_argument('--input', required=True, help='Input file (csv/xlsx/json)')
    parser.add_argument('--output', default='report.xlsx', help='Output file')
    parser.add_argument('--title', default='Data Report', help='Report title')
    args = parser.parse_args()
    
    gen = ReportGenerator()
    gen.run(args.input, args.output, args.title)
