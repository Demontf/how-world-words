from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.colors import Color
from reportlab.pdfbase.ttfonts import TTFont
import textwrap
import os
from pathlib import Path

file_name = "mars"

class BilingualPDFGenerator:
    def __init__(self, output_path):
        self.output_path = Path(output_path).absolute()
        
        self.page_width, self.page_height = A4
        self.margin = 20
        self.line_height = 15
        
        self.english_chars_per_line = 58
        self.chinese_chars_per_line = 18
        
        # Register fonts
        #pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        #pdfmetrics.registerFont(TTFont('MicrosoftYaHei', 'msyh.ttc'))  # msyh.ttc 是微软雅黑字体文件
        pdfmetrics.registerFont(TTFont('SourceHanSerif', './SourceHanSerif-VF.ttf'))
        
        
        self.pdf = canvas.Canvas(str(self.output_path), pagesize=A4)
        
        # Define font settings for both languages
        self.english_font = 'Helvetica'
        #self.chinese_font = 'MicrosoftYaHei'
        self.chinese_font = 'SourceHanSerif'
        self.font_size = 12
        
        total_usable_width = self.page_width - (2 * self.margin)
        self.middle_gap = 10
        
        self.left_column_width = (total_usable_width - self.middle_gap) * 0.60
        self.right_column_width = (total_usable_width - self.middle_gap) * 0.40
        
        self.left_column_x = self.margin
        self.right_column_x = self.margin + self.left_column_width + self.middle_gap
    
    def draw_column_lines(self):
        light_gray = Color(0.8, 0.8, 0.8, alpha=0.5)
        self.pdf.setStrokeColor(light_gray)
        self.pdf.setLineWidth(0.5)
        
        center_x = self.page_width / 2
        self.pdf.line(center_x, self.margin, center_x, self.page_height - self.margin)
        
        self.pdf.setStrokeColor(Color(0, 0, 0, alpha=1))
    
    def draw_text_with_font(self, text, x, y, is_english=True):
        """Helper method to draw text with appropriate font"""
        if is_english:
            self.pdf.setFont(self.english_font, self.font_size)
        else:
            self.pdf.setFont(self.chinese_font, self.font_size)
        self.pdf.drawString(x, y, text)
    
    def process_text_files(self, english_file, chinese_file):
        try:
            with open(english_file, 'r', encoding='utf-8') as f:
                english_text = f.read().split('\n')
            
            with open(chinese_file, 'r', encoding='utf-8') as f:
                chinese_text = f.read().split('\n')
            
            current_y = self.page_height - self.margin
            
            for en, zh in zip(english_text, chinese_text):
                en_wrapped = textwrap.fill(en, width=self.english_chars_per_line)
                zh_wrapped = textwrap.fill(zh, width=self.chinese_chars_per_line)
                
                en_lines = en_wrapped.split('\n')
                zh_lines = zh_wrapped.split('\n')
                
                needed_height = max(len(en_lines), len(zh_lines)) * self.line_height
                
                if current_y - needed_height < self.margin:
                    self.pdf.showPage()
                    #self.draw_column_lines()
                    current_y = self.page_height - self.margin
                
                # Draw English text (left column) with Helvetica
                temp_y = current_y
                for line in en_lines:
                    self.draw_text_with_font(line, self.left_column_x, temp_y, is_english=True)
                    temp_y -= self.line_height
                
                # Draw Chinese text (right column) with STSong-Light
                temp_y = current_y
                for line in zh_lines:
                    self.draw_text_with_font(line, self.right_column_x, temp_y, is_english=False)
                    temp_y -= self.line_height
                
                current_y -= needed_height + 1
            
            self.pdf.save()
            print(f"PDF file generated successfully: {self.output_path}")
            
        except Exception as e:
            print(f"Error processing files: {e}")
            raise

def main():
    current_dir = Path.cwd()
    output_pdf = current_dir / 'mars.pdf'
    eng_file_path = file_name+'.txt'
    ch_file_path = file_name+'_ch.txt'
    
    try:
        generator = BilingualPDFGenerator(output_pdf)
        generator.process_text_files(str(current_dir / eng_file_path), str(current_dir / ch_file_path))
        
    except Exception as e:
        print(f"Program execution error: {e}")

if __name__ == '__main__':
    main()