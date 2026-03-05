import os
import re

md_file = 'Solar_PV_Forecasting_Journal_Paper.md'

with open(md_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the entire section 3.2 Missing Value Analysis
section_32_pattern = r'### 3\.2 Missing Value Analysis\n\n.*?(?=### 3\.3)'
text = re.sub(section_32_pattern, '', text, flags=re.DOTALL)

# Re-number the sections and figures
text = text.replace('### 3.3 Univariate Analysis', '### 3.2 Univariate Analysis')
text = text.replace('### 3.4 Bivariate and Correlation Analysis', '### 3.3 Bivariate and Correlation Analysis')
text = text.replace('### 3.5 Time-Series Patterns', '### 3.4 Time-Series Patterns')

text = text.replace('Figure 2', 'Figure 1')
text = text.replace('Figure 3', 'Figure 2')
text = text.replace('Figure 4', 'Figure 3')
text = text.replace('Figure 5', 'Figure 4')

# Save updated markdown
with open(md_file, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated Markdown: removed unnecessary missing values chart and renumbered sections/figures.")

# Next, let's update convert_to_pdf.py to make figures 100% linewidth
pdf_script = 'convert_to_pdf.py'
with open(pdf_script, 'r', encoding='utf-8') as f:
    pdf_text = f.read()

pdf_text = pdf_text.replace('width=0.95\\linewidth', 'width=1.0\\linewidth')
pdf_text = pd_text = pdf_text.replace('"geometry:margin=0.8in"', '"geometry:margin=0.7in"') # even smaller margin = bigger text area

with open(pdf_script, 'w', encoding='utf-8') as f:
    f.write(pdf_text)

print("Updated convert_to_pdf.py for max width.")

# Next, update Word generator to max width (around 7 inches for standard page)
word_script = 'generate_word_report.py'
if os.path.exists(word_script):
    with open(word_script, 'r', encoding='utf-8') as f:
        word_text = f.read()
    word_text = word_text.replace('Inches(6.7)', 'Inches(7.2)')
    
    with open(word_script, 'w', encoding='utf-8') as f:
        f.write(word_text)
    print("Updated Word converter for max width.")
