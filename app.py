import openai
import polib
import os
import json
import openai.error
import re
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da API Key da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Caminho do arquivo PO a ser modificado
caminho_arquivo_po = os.getenv("CAMINHO_ARQUIVO_PO", "caminho/para/seu/arquivo.po")
# Caminho do arquivo que irá registrar o progresso
caminho_progresso = os.getenv("CAMINHO_PROGRESSO", "progresso.json")

# Função para traduzir e/ou corrigir uma string usando a API OpenAI
def traduzir_string(texto, contexto="vagas de emprego"):
    prompt = (
        f"Traduza o seguinte texto para o português brasileiro, mantendo o contexto e adaptando quando necessário, mas sem adicionar informações que não estão no original: \n"
        f"Texto original: {texto}\n"
        "Texto traduzido:"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.5,
        )
        traducao = response.choices[0].message['content'].strip()
        # Verificar se a tradução contém adições desnecessárias
        if "não precisa ser corrigido" in traducao.lower() or "referência a" in traducao.lower() or re.match(r"^[^a-zA-Z]*$", traducao):
            print(f"Aviso: Tradução incorreta detectada para '{texto}'. Utilizando texto original.")
            return texto
        return traducao
    except openai.error.RateLimitError:
        print("Erro: Limite de uso da API atingido. Por favor, aguarde e tente novamente mais tarde.")
        return texto
    except openai.error.OpenAIError as e:
        print(f"Erro na API OpenAI: {e}")
        return texto

# Função para carregar o progresso já existente
def carregar_progresso():
    if os.path.exists(caminho_progresso):
        with open(caminho_progresso, 'r') as arquivo:
            return json.load(arquivo)
    return {}

# Função para salvar o progresso
def salvar_progresso(indice_atual):
    with open(caminho_progresso, 'w') as arquivo:
        json.dump({"indice": indice_atual}, arquivo)

# Carregar o arquivo PO com o polib
po = polib.pofile(caminho_arquivo_po)

# Gerar o nome do arquivo corrigido com base no original
nome_arquivo_corrigido = caminho_arquivo_po.replace(".po", "_arquivo_corrigido.po")

# Carregar o progresso já existente
progresso = carregar_progresso()
indice_inicial = progresso.get("indice", 0)

# Percorrer as entradas do arquivo PO a partir do ponto salvo
for i, entrada in enumerate(po):
    if i < indice_inicial:
        continue
    
    # Verifica se msgid existe e msgstr está vazio ou precisa ser corrigido
    if entrada.msgid:
        # Pular entradas que não têm texto traduzível ou são apenas placeholders
        if re.match(r"^[^a-zA-Z]*$", entrada.msgid) or re.match(r"^%[a-zA-Z]*$", entrada.msgid) or not re.search(r"[a-zA-Z]", entrada.msgid):
            print(f"Pulando linha {i + 1}: msgid: {entrada.msgid}, pois não contém texto traduzível.")
            continue
        
        # Log da linha e do conteúdo a ser traduzido
        print(f"Traduzindo linha {entrada.linenum}: msgid: {entrada.msgid}, msgstr atual: {entrada.msgstr}")
        # Traduz ou corrige a string existente no msgstr com base no msgid
        nova_traducao = traduzir_string(entrada.msgid)
        print(f"Nova tradução: {nova_traducao}")
        entrada.msgstr = nova_traducao
        
        # Salvar progresso após cada tradução
        salvar_progresso(i)
        
        # Salvar o arquivo PO conforme ele é traduzido
        po.save(nome_arquivo_corrigido)

print(f"Tradução e correção concluída. Arquivo salvo como '{nome_arquivo_corrigido}'")
