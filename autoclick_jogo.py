import pyautogui
import time

clique_posicoes = [
    (843, 950),
    (909, 950),
    (995, 950),
    (1076, 950),
]

intervalo = 2  # segundos entre os cliques

print("Auto clicker iniciado. Pressione Ctrl+C para parar...")

try:
    while True:
        for pos in clique_posicoes:
            pyautogui.click(pos[0], pos[1])  # Clique nas coordenadas
            print(f"Clique em {pos}. Esperando {intervalo}s...")
            time.sleep(intervalo)
except KeyboardInterrupt:
    print("Auto clicker finalizado.")