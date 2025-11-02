# modules/whatsapp_automator.py

import pyautogui
import pygetwindow as gw
import time
import os
import platform

pyautogui.FAILSAFE = True

def open_whatsapp():
    """Abre o app do WhatsApp e o traz para o foco."""
    try:
        # Tenta encontrar a janela do WhatsApp. O título pode variar.
        # Use gw.getAllTitles() em um print para descobrir o título exato se falhar.
        whatsapp_window = gw.getWindowsWithTitle('WhatsApp')[0]
        if not whatsapp_window.isActive:
            whatsapp_window.activate()
        if not whatsapp_window.isMaximized:
            whatsapp_window.maximize()
        time.sleep(1)
        return whatsapp_window
    except IndexError:
        try:
            if platform.system() == "Windows":
                os.system('start shell:appsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App')
                time.sleep(5)
                return open_whatsapp()
            # Adicionar comandos para outros OS aqui se necessário
            return None
        except Exception:
            return None

def find_and_click(image_name, confidence=0.9):
    """
    Procura por uma imagem na tela, retorna sua localização e clica nela.
    """
    try:
        image_path = os.path.join('assets', image_name)
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.click(location)
            time.sleep(0.5)
            return location # Retorna as coordenadas do clique
        else:
            print(f"Imagem '{image_name}' não encontrada na tela.")
            return None
    except Exception as e:
        print(f"Erro ao procurar a imagem '{image_name}': {e}")
        return None

def send_message_to_contact(contact_name, message):
    """
    Orquestra a automação usando a barra de pesquisa.
    """
    if not open_whatsapp():
        return "Não consegui abrir ou encontrar o WhatsApp."

    # 1. Encontra e clica na barra de pesquisa
    search_bar_location = find_and_click('whatsapp_search_bar.png')
    if not search_bar_location:
        return "Não encontrei a barra de pesquisa do WhatsApp. Verifique o recorte em 'assets/whatsapp_search_bar.png'."

    # 2. Digita o nome do contato na barra de pesquisa
    pyautogui.write(contact_name, interval=0.1)
    time.sleep(2) # ESSENCIAL: Espera o WhatsApp filtrar os resultados

    # 3. Clica no primeiro resultado
    # O primeiro resultado geralmente aparece a uma distância fixa abaixo da barra de pesquisa.
    # Este valor (y_offset) pode precisar de ajuste dependendo da sua resolução de tela.
    y_offset = 70 
    pyautogui.click(search_bar_location.x, search_bar_location.y + y_offset)
    time.sleep(1)

    # 4. Digita e envia a mensagem
    pyautogui.write(message, interval=0.05)
    pyautogui.press('enter')

    return f"Mensagem enviada para {contact_name}."