from fpdf import FPDF
from math import sin, cos, pi
import re

def write_to_file(query, content):
    with open("output.txt", "a", encoding='utf-8') as f:
        f.write("Q: " + query.capitalize() + "\n")
        f.write("A: " + content + '\n')
    
def read_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    qa_pairs = re.findall(r'Q:(.*?)\nA:(.*?)(?=\nQ:|\Z)', content, re.S)
    qa_pairs = [(q.strip(), a.strip()) for q, a in qa_pairs]
    return qa_pairs

# Function to write questions and answers to a pdf file
class PDF(FPDF):

    title = "Cobra.ai"
    def header(self):
        self.set_font('Arial', 'B', 18)
        self.cell(0, 20, self.title, 0, 1, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.multi_cell(0, 10, label)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def footer(self):
        self.set_font('Arial', 'B', 7)
        self.cell(0, 10, 'Cobra.ai', 0, 1, 'R')

    def add_pair(self, question, answer):
        self.chapter_title(f'Q: {question}')
        self.chapter_body(f'A: {answer}')

    def add_watermark(self, text):
        self.set_font('Arial', 'B', 50)
        self.set_text_color(200, 200, 200)
        self.rotate(45)
        self.set_xy(0, 0)
        self.cell(w=210, h=297, txt=text, border=0, align='C', ln=0)
        self.rotate(0)

    def rotate(self, angle, x=None, y=None):
        if x is None:
            x = self.get_x()
        if y is None:
            y = self.get_y()
        self._out('q')
        self._out(f'1 0 0 1 {x * self.k:.2f} {y * self.k:.2f} cm')
        self._out(f'{cos(angle * pi / 180):.2f} {sin(angle * pi / 180):.2f} {-sin(angle * pi / 180):.2f} {cos(angle * pi / 180):.2f} 0 0 cm')
        self._out(f'{-x * self.k:.2f} {-y * self.k:.2f} cm')

    def end_page(self):
        super().end_page()
        self.add_watermark('cobra.AI')

def main(file="output.txt", target="output.pdf"):
    qa_pairs = read_from_file(file)
    pdf = PDF()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()

    for question, answer in qa_pairs:
        pdf.add_pair(question, answer)

    pdf.output(target)

if __name__ == '__main__':
    
    main()