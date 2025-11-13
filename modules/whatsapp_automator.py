import pyautogui
import pygetwindow as gw
import time
import os
import platform
import subprocess

pyautogui.FAILSAFE = True

def open_whatsapp():
    """Abre o app do WhatsApp e o traz para o foco. Retorna uma string de status."""
    try:
        whatsapp_window = gw.getWindowsWithTitle('WhatsApp')[0]
        
        if whatsapp_window.isMinimized:
            whatsapp_window.restore()
        
        whatsapp_window.activate()
        whatsapp_window.maximize()
        
        time.sleep(1)
        return "WhatsApp ativado."
    except IndexError:
        try:
            if platform.system() == "Windows":
                command = 'start shell:appsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App'
                os.system(command)
                
                start_time = time.time()
                whatsapp_window = None
                while time.time() - start_time < 10:
                    try:
                        whatsapp_window = gw.getWindowsWithTitle('WhatsApp')[0]
                        break 
                    except IndexError:
                        time.sleep(0.5)
                
                if whatsapp_window:
                    whatsapp_window.activate()
                    whatsapp_window.maximize()
                    return "WhatsApp iniciado e ativado."
                else:
                    return "WhatsApp iniciado, mas não consegui ativar a janela."
            return "Não foi possível iniciar o WhatsApp no seu sistema."
        except Exception as e:
            print(f"Erro ao tentar iniciar o WhatsApp: {e}")
            return "Não consegui encontrar ou iniciar o WhatsApp."

def find_and_click(image_names, confidence=0.8):
    """
    Procura por uma lista de imagens na tela, retorna a localização da primeira que encontrar e clica nela.
    """
    if not isinstance(image_names, list):
        image_names = [image_names]

    for image_name in image_names:
        try:
            image_path = os.path.join('assets', image_name)
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location:
                pyautogui.click(location)
                time.sleep(0.5)
                return location 
        except Exception as e:
            print(f"Erro ao procurar a imagem '{image_name}': {e}")
            continue
    
    print(f"Nenhuma das imagens {image_names} foi encontrada na tela.")
    return None

def send_message_to_contact(contact_name, message):

    status_or_error = open_whatsapp()
    if "ativado" not in status_or_error:
        return status_or_error

    time.sleep(1)

    search_bar_images = ['whatsapp_search_bar.png', 'whatsapp_search_bar_2.png']
    search_bar_location = find_and_click(search_bar_images, confidence=0.8)
    if not search_bar_location:
        return "Não encontrei a barra de pesquisa do WhatsApp. Verifique os recortes em 'assets/'."

    pyautogui.write(contact_name, interval=0.1)
    time.sleep(2) 

    y_offset = 70 
    pyautogui.click(search_bar_location.x, search_bar_location.y + y_offset)
    time.sleep(1)

    pyautogui.write(message, interval=0.05)
    pyautogui.press('enter')

    return f"Mensagem enviada para {contact_name}."