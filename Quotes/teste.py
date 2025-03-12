from rembg import remove
from PIL import Image

#Caminho da Imagem
input_path = 'static/selos.png'
# Caminho para salvar a imagem sem fundo
output_path = 'imagem_sem_fundo.png'
# Abrir a imagem no Python
input = Image.open(input_path)

# Comando mágico que remove o fundo
output = remove(input)
# Salvar a imagem
output.save(output_path)