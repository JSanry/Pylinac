import steamlit as st
st.markdown('''
#EXIBIR

## UPLOAD O SEU ARQUIVO
''')

arquivo = st.file_uploader(
	'Suba seu arquivo!'
	type=['jpg', 'png']
) 
