import pyautogui
import time
import cv2
import numpy as np

#organizar cada skill e seus intervalos
template_ataque = "skill_1.png"  #imagem do botão ou do inimigo
threshold = 0.8  #precisão da imagem
intervalo_entre_habilidades = 2  #tempo entre cada skill
intervalo_ciclo = 3  #tempo entre ciclos de ataque

def localizar_elemento(template_path, threshold=0.8):   #localizar os itens da tela
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    template = cv2.imread(template_path, 0)
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        return max_loc  #coordenadas (x, y)
    else:
        return None

def clicar_em(imagem):
    pos = localizar_elemento(imagem, threshold)
    if pos:
        pyautogui.click(pos[0] + 10, pos[1] + 10)  #clica no centro aproximado
        return True
    return False

def usar_habilidades(intervalo=2):
    habilidades = ['1', '2', '3', '4', '5']
    for tecla in habilidades:
        pyautogui.press(tecla)
        time.sleep(intervalo)

#principal
print("Bot iniciado. Pressione Ctrl+C para parar.")
try:
    while True:
        if clicar_em(template_ataque):
            print("Inimigo encontrado e clicado.")
        else:
            print("Inimigo não encontrado.")
        
        usar_habilidades(intervalo_entre_habilidades)
        time.sleep(intervalo_ciclo)

except KeyboardInterrupt:
    print("Bot encerrado pelo usuário.")