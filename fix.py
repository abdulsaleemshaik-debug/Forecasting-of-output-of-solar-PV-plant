import os
with open('Solar_PV_Forecasting_Journal_Paper.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Manual mapping of common UTF-8 -> Windows-1252 mojibake
text = text.replace('â€“', '-')
text = text.replace('Â²', '²')
text = text.replace('â€œ', '"')
text = text.replace('â€', '"')
text = text.replace('â€™', "'")
text = text.replace('Â', '')
text = text.replace('Ã—', 'x')

with open('Solar_PV_Forecasting_Journal_Paper.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Formatting repaired!")
