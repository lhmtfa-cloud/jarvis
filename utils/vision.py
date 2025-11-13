import pyautogui
import pytesseract
import pyperclip
import operator
import time
import os
import traceback
from PIL import Image, ImageOps, ImageChops

_falar = None
IMG_FOLDER = 'img'

def inicializar(falar_func):
    global _falar
    _falar = falar_func
    if not os.path.exists(IMG_FOLDER):
        os.makedirs(IMG_FOLDER)
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\rafae\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    except Exception as e:
        print(f"AVISO: Tesseract não configurado: {e}")

def preprocessar_para_ocr(imagem):
    imagem_em_escala_de_cinza = imagem.convert('L')
    return imagem_em_escala_de_cinza

def _costurar_texto(lista_de_textos):
    if not lista_de_textos: return ""
    texto_final = lista_de_textos[0]
    for i in range(1, len(lista_de_textos)):
        texto_anterior, texto_atual = texto_final, lista_de_textos[i]
        ancora = texto_anterior[-50:].strip()
        if not ancora:
            texto_final += "\n" + texto_atual
            continue
        ponto_de_costura = texto_atual.find(ancora)
        if ponto_de_costura != -1:
            texto_final += texto_atual[ponto_de_costura + len(ancora):]
        else:
            texto_final += "\n" + texto_atual
    return texto_final

def copiar_texto_delimitado(texto_inicio, texto_fim, region=None):
    _falar(f"Iniciando cópia de texto entre '{texto_inicio}' e '{texto_fim}'.")
    try:
        texto_inicio_lower, texto_fim_lower = texto_inicio.lower(), texto_fim.lower()
        textos_dos_blocos = []
        screenshot_inicial = pyautogui.screenshot(region=region)
        texto_inicial_completo = pytesseract.image_to_string(preprocessar_para_ocr(screenshot_inicial), lang='por').lower()
        ponto_de_partida = texto_inicial_completo.find(texto_inicio_lower)
        if ponto_de_partida == -1:
            return _falar(f"Não encontrei a palavra de início: '{texto_inicio}'")
        ponto_final_inicial = texto_inicial_completo.find(texto_fim_lower, ponto_de_partida)
        if ponto_final_inicial != -1:
            texto_para_copiar = texto_inicial_completo[ponto_de_partida : ponto_final_inicial + len(texto_fim_lower)]
            pyperclip.copy(texto_para_copiar); _falar("Texto copiado com sucesso.")
            return
        textos_dos_blocos.append(texto_inicial_completo[ponto_de_partida:])
        _falar("Ponto de início encontrado. Rolando para procurar o fim...")
        tentativas_rolagem, max_tentativas, ultima_imagem_da_tela = 0, 20, screenshot_inicial
        while tentativas_rolagem < max_tentativas:
            pyautogui.scroll(-700); time.sleep(1.5)
            screenshot_atual = pyautogui.screenshot(region=region)
            texto_atual = pytesseract.image_to_string(preprocessar_para_ocr(screenshot_atual), lang='por').lower()
            ponto_final = texto_atual.find(texto_fim_lower)
            if ponto_final != -1:
                _falar("Ponto de fim encontrado.")
                textos_dos_blocos.append(texto_atual[:ponto_final + len(texto_fim_lower)])
                break
            else:
                _falar(f"Analisando tela... (tentativa {tentativas_rolagem + 1})")
                textos_dos_blocos.append(texto_atual)
            diff = ImageChops.difference(ultima_imagem_da_tela.convert('RGB'), screenshot_atual.convert('RGB'))
            if not diff.getbbox():
                _falar("Detectei o fim da página, mas não encontrei a palavra de fim.")
                break
            ultima_imagem_da_tela = screenshot_atual
            tentativas_rolagem += 1
        else:
            return _falar(f"Não encontrei a palavra de fim '{texto_fim}' após rolar a tela.")
        _falar("Processando e costurando o texto coletado.")
        texto_unido = _costurar_texto(textos_dos_blocos)
        if texto_unido.strip():
            pyperclip.copy(texto_unido); _falar("Texto final montado e copiado para a área de transferência.")
        else:
            _falar("Não encontrei texto legível para copiar.")
    except Exception:
        _falar("Ocorreu um erro crítico durante a operação de cópia de texto.")
        traceback.print_exc()

def selecionar_texto_delimitado(texto_inicio, texto_fim, region=None):
    _falar(f"Iniciando seleção inteligente de '{texto_inicio}' até '{texto_fim}'.")
    try:
        screenshot = pyautogui.screenshot(region=region)
        data = pytesseract.image_to_data(preprocessar_para_ocr(screenshot), lang='por', output_type=pytesseract.Output.DICT)
        words = [d.lower() for i, d in enumerate(data['text']) if d.strip() != '' and int(data['conf'][i]) > 30]
        original_indices = [i for i, d in enumerate(data['text']) if d.strip() != '' and int(data['conf'][i]) > 30]
        start_indices = [i for i, word in enumerate(words) if texto_inicio.lower() in word]
        if not start_indices:
            return _falar(f"Não encontrei a palavra de início: '{texto_inicio}'")
        
        start_idx_original = original_indices[start_indices[0]]
        start_coords = (data['left'][start_idx_original] + (region[0] if region else 0), data['top'][start_idx_original] + (region[1] if region else 0) + data['height'][start_idx_original] // 2)
        
        pyautogui.moveTo(start_coords)
        pyautogui.mouseDown(button='left')
        _falar("Ponto de início encontrado. Rolando para procurar o fim...")
        time.sleep(0.5)

        tentativas_rolagem, max_tentativas, encontrou_fim = 0, 20, False
        
        while tentativas_rolagem < max_tentativas:
            screenshot_atual = pyautogui.screenshot(region=region)
            data_atual = pytesseract.image_to_data(preprocessar_para_ocr(screenshot_atual), lang='por', output_type=pytesseract.Output.DICT)
            words_atuais = [d.lower() for i, d in enumerate(data_atual['text']) if d.strip() != '' and int(data_atual['conf'][i]) > 30]
            original_indices_atuais = [i for i, d in enumerate(data_atual['text']) if d.strip() != '' and int(data_atual['conf'][i]) > 30]
            end_indices = [i for i, word in enumerate(words_atuais) if texto_fim.lower() in word]

            if end_indices:
                _falar("Ponto de fim encontrado.")
                end_idx_original = original_indices_atuais[max(end_indices)]
                end_coords = (data_atual['left'][end_idx_original] + data_atual['width'][end_idx_original] + (region[0] if region else 0), data_atual['top'][end_idx_original] + data_atual['height'][end_idx_original] // 2 + (region[1] if region else 0))
                pyautogui.moveTo(end_coords, duration=0.5)
                encontrou_fim = True
                break
            
            _falar(f"Analisando tela... (tentativa {tentativas_rolagem + 1})")
            
            current_x, _ = pyautogui.position()
            pyautogui.moveTo(current_x, pyautogui.size()[1] - 20, duration=0.2)
            time.sleep(1.5)
            
            tentativas_rolagem += 1

        if not encontrou_fim:
            _falar("Não encontrei a palavra de fim após rolar, selecionando até o fim da tela.")
        
    finally:
        pyautogui.mouseUp(button='left')
        _falar("Seleção concluída.")

def copiar_texto_da_imagem(nome_imagem):
    _falar(f"Procurando '{nome_imagem}' para ler o texto.")
    try:
        if not nome_imagem.endswith('.png'): nome_imagem += '.png'
        full_path = os.path.join(IMG_FOLDER, nome_imagem)
        local_imagem = pyautogui.locateOnScreen(full_path, confidence=0.8)
        if local_imagem:
            texto_extraido = pytesseract.image_to_string(preprocessar_para_ocr(pyautogui.screenshot(region=local_imagem)), lang='por')
            if texto_extraido.strip():
                pyperclip.copy(texto_extraido.strip()); _falar(f"Texto '{texto_extraido.strip()}' copiado.")
            else: _falar("Não encontrei texto legível na imagem.")
        else: _falar(f"Não encontrei a imagem '{nome_imagem}' na tela.")
    except Exception: _falar(f"Erro ao ler texto da imagem.")

def clicar_na_imagem(nome_imagem):
    _falar(f"Procurando '{nome_imagem}' para clicar.")
    try:
        if not nome_imagem.endswith('.png'): nome_imagem += '.png'
        full_path = os.path.join(IMG_FOLDER, nome_imagem)
        local_imagem = pyautogui.locateOnScreen(full_path, confidence=0.8)
        if local_imagem:
            pyautogui.click(pyautogui.center(local_imagem)); _falar("Imagem encontrada e clicada.")
        else: _falar(f"Não consegui encontrar a imagem '{nome_imagem}' na tela.")
    except Exception: _falar(f"Erro ao procurar pela imagem.")

def colar_texto():
    _falar("Colando."); pyautogui.hotkey('ctrl', 'v')

def esperar(argumentos_str):
    try:
        segundos = float(argumentos_str.split()[0])
        _falar(f"Ok, esperando por {segundos} segundos."); time.sleep(segundos)
        _falar("Espera finalizada.")
    except Exception: _falar("Não entendi por quantos segundos devo esperar.")

def digitar_em_caixa_generica(texto_para_digitar):
    _falar("Procurando por uma caixa de texto conhecida...")
    modelos = ['caixa_branca.png', 'caixa_pesquisa_google.png', 'caixa_whatsapp.png', 'caixa_escura.png', 'caixa_de_texto.png']
    for modelo in modelos:
        try:
            local_caixa = pyautogui.locateOnScreen(os.path.join(IMG_FOLDER, modelo), confidence=0.8)
            if local_caixa:
                _falar(f"Caixa do tipo '{modelo}' encontrada.")
                pyautogui.click(pyautogui.center(local_caixa)); time.sleep(0.5)
                pyautogui.write(texto_para_digitar, interval=0.05)
                _falar("Texto digitado.")
                return
        except Exception: continue
    _falar("Não encontrei nenhuma caixa de texto conhecida na tela.")

def criar_arquivo_txt(nome_arquivo, conteudo):
    try:
        with open(f"{nome_arquivo}.txt", "w", encoding='utf-8') as f: f.write(conteudo)
        _falar(f"Arquivo '{nome_arquivo}' criado.")
    except Exception as e: _falar("Não foi possível criar o arquivo."); print(e)

def comparar_valores(v1_str, op_str, v2_str):
    try:
        v1, v2 = float(v1_str), float(v2_str)
        ops = {"igual a": operator.eq, "diferente de": operator.ne, "maior que": operator.gt, "menor que": operator.lt}
        op_func = ops.get(op_str)
        if op_func: _falar("Verdadeiro" if op_func(v1, v2) else "Falso")
        else: _falar("Operador de comparação não reconhecido.")
    except Exception: _falar("Não entendi os valores para comparar.")

def calcular_valores(v1_str, op_str, v2_str):
    try:
        v1, v2 = float(v1_str), float(v2_str)
        ops = {"mais": operator.add, "+": operator.add, "menos": operator.sub, "-": operator.sub, "vezes": operator.mul, "*": operator.mul, "dividido por": operator.truediv, "/": operator.truediv}
        op_func = next((v for k, v in ops.items() if k in op_str), None)
        if op_func: _falar(f"O resultado é {op_func(v1, v2)}")
        else: _falar("Operação matemática não reconhecida.")
    except Exception: _falar("Não entendi os valores para calcular.")

def copiar_selecao():
    _falar("Copiando seleção.")
    try:
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.2)
    except Exception as e:
        _falar("Ocorreu um erro ao tentar copiar.")
        print(f"Erro em copiar_selecao: {e}")