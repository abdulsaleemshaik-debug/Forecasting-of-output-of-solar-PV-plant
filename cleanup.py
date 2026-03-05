import re

md_file = 'Solar_PV_Forecasting_Journal_Paper.md'

with open(md_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Pattern for 3.2
pattern = r'### 3\.2 Missing Value Analysis.*?### 3\.3 Univariate Analysis'
text = re.sub(pattern, '### 3.2 Univariate Analysis', text, flags=re.DOTALL)

# Re-number remaining sections 3.X
text = text.replace('### 3.4 Bivariate and Correlation Analysis', '### 3.3 Bivariate and Correlation Analysis')
text = text.replace('### 3.5 Time-Series Patterns', '### 3.4 Time-Series Patterns')

# Re-number Figures in the text
text = text.replace('Figure 2', 'Figure 1')
text = text.replace('Figure 3', 'Figure 2')
text = text.replace('Figure 4', 'Figure 3')
text = text.replace('Figure 5', 'Figure 4')

# Re-number 'Figure 1 - Missing Value Analysis' was already removed by the regex replacement!
# So we only needed to rename 2->1, 3->2, etc.

with open(md_file, 'w', encoding='utf-8') as f:
    f.write(text)

print("Done")
