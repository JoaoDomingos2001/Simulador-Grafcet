import tkinter as tk
from tkinter import messagebox
import time
import collections

class SimuladorGrafcetCompleto:
    def __init__(self, root):
        self.root = root
        self.root.title("Laboratório de Automação: Estudo de Qualificadores")
        self.root.geometry("1200x900")
        self.root.configure(bg="#050505")

        # --- ESTADO E CONFIGURAÇÕES ---
        self.etapa_ativa = False
        self.qualificador = "S"
        self.output = False
        self.condicao_c = False
        self.start_time = 0
        
        # Tempos conforme a norma (image_13 e image_14)
        self.t_atraso = 2.0  # D = 2s
        self.t_limite = 3.0  # L = 3s
        
        # Dados para o Gráfico
        self.hist_etapa = collections.deque([0]*100, maxlen=100)
        self.hist_saida = collections.deque([0]*100, maxlen=100)

        self.setup_ui()
        self.engine()

    def setup_ui(self):
        # 1. Painel de Seleção Superior
        self.top = tk.Frame(self.root, bg="#111", pady=10)
        self.top.pack(fill="x")
        
        explicao_btn = { "width": 15, "bg": "#222", "fg": "white", "relief": "flat", "font": ("Arial", 9, "bold") }
        for q in ["S", "D", "L", "P", "C"]:
            tk.Button(self.top, text=f"Qualificador {q}", command=lambda v=q: self.set_q(v), **explicao_btn).pack(side="left", padx=10)

        # 2. Área de Explicação (Dinâmica)
        self.info_box = tk.Frame(self.root, bg="#002244", pady=10)
        self.info_box.pack(fill="x", padx=20, pady=5)
        self.lbl_teoria = tk.Label(self.info_box, text="", bg="#002244", fg="white", font=("Arial", 10), justify="left")
        self.lbl_teoria.pack()

        # 3. Canvas Principal (Grafcet + Gráfico)
        self.main_canvas = tk.Frame(self.root, bg="#050505")
        self.main_canvas.pack(fill="both", expand=True, padx=20)
        
        self.cv_graf = tk.Canvas(self.main_canvas, width=400, height=400, bg="#080808", highlightthickness=1)
        self.cv_graf.grid(row=0, column=0, padx=10)
        
        self.cv_plot = tk.Canvas(self.main_canvas, width=700, height=400, bg="#050505", highlightthickness=0)
        self.cv_plot.grid(row=0, column=1, padx=10)

        # 4. Consola de Controlo
        self.ctrl = tk.Frame(self.root, bg="#111", height=150)
        self.ctrl.pack(fill="x", side="bottom")

        self.btn_in = tk.Button(self.ctrl, text="ATIVAR ETAPA", bg="#004400", fg="white", font=("Arial", 12, "bold"), width=20)
        self.btn_in.pack(side="left", padx=50, pady=20)
        self.btn_in.bind("<ButtonPress-1>", lambda e: self.set_in(True))
        self.btn_in.bind("<ButtonRelease-1>", lambda e: self.set_in(False))

        self.chk_c = tk.Checkbutton(self.ctrl, text="Condição (C)", bg="#111", fg="white", selectcolor="black", command=self.toggle_c)
        self.chk_c.pack(side="left")

        self.lbl_timer = tk.Label(self.ctrl, text="TIMER: 0.0s", bg="#111", fg="yellow", font=("Consolas", 15))
        self.lbl_timer.pack(side="right", padx=50)

        self.set_q("S") # Início

    def set_q(self, q):
        self.qualificador = q
        self.output = False if q != "S" else self.output
        
        teoria = {
            "S": "S - Stored: Ação mantém-se ativa mesmo após a etapa ser desativada.",
            "D": f"D - Delayed: Ação só inicia após um atraso temporal (T = {self.t_atraso}s).",
            "L": f"L - Time Limited: Ação inicia com a etapa, mas termina após T = {self.t_limite}s.",
            "P": "P - Pulse Shaped: Ação executada apenas no instante (pulso) de ativação.",
            "C": "C - Condition: Ação só executada se a etapa estiver ativa E a condição for verdadeira."
        }
        self.lbl_teoria.config(text=teoria[q])

    def set_in(self, val):
        if val: self.start_time = time.time()
        self.etapa_ativa = val

    def toggle_c(self): self.condicao_c = not self.condicao_c

    def engine(self):
        now = time.time()
        elapsed = now - self.start_time if self.etapa_ativa else 0

        # Lógica de Qualificadores
        if self.qualificador == "S":
            if self.etapa_ativa: self.output = True # Armazena
        elif self.qualificador == "D":
            self.output = True if (self.etapa_ativa and elapsed >= self.t_atraso) else False # Atraso
        elif self.qualificador == "L":
            self.output = True if (self.etapa_ativa and elapsed <= self.t_limite) else False # Limite
        elif self.qualificador == "P":
            self.output = True if (self.etapa_ativa and 0 < elapsed < 0.1) else False # Pulso
        elif self.qualificador == "C":
            self.output = self.etapa_ativa and self.condicao_c # Condição

        self.hist_etapa.append(1 if self.etapa_ativa else 0)
        self.hist_saida.append(1 if self.output else 0)
        
        self.render(elapsed)
        self.root.after(40, self.engine)

    def render(self, t):
        self.cv_graf.delete("all")
        self.cv_plot.delete("all")
        
        # --- 1. Desenho do Grafcet (Mantido) ---
        x, y = 100, 150
        cor = "#00ff00" if self.etapa_ativa else "#333"
        self.cv_graf.create_rectangle(x, y, x+50, y+50, outline=cor, width=2)
        self.cv_graf.create_text(x+25, y+25, text="1", fill="white")
        self.cv_graf.create_line(x+50, y+25, x+80, y+25, fill="white")
        self.cv_graf.create_rectangle(x+80, y, x+120, y+50, outline="#00ff00") 
        self.cv_graf.create_text(x+100, y+25, text=self.qualificador, fill="white")
        self.cv_graf.create_rectangle(x+120, y, x+250, y+50, outline="white") 
        self.cv_graf.create_text(x+185, y+25, text="Motor_M1", fill="white")
        
        # --- 2. Desenho do Cronograma com Grelha ---
        # Definição de alturas para os níveis 0 e 1
        y_etapa_0, y_etapa_1 = 120, 70
        y_saida_0, y_saida_1 = 320, 270

        # Desenhar Grelha Horizontal e Etiquetas de Nível
        # Para a Etapa
        self.cv_plot.create_line(50, y_etapa_0, 700, y_etapa_0, fill="#222", dash=(4, 4)) # Nível 0
        self.cv_plot.create_line(50, y_etapa_1, 700, y_etapa_1, fill="#222", dash=(4, 4)) # Nível 1
        self.cv_plot.create_text(40, y_etapa_0, text="0", fill="#666", font=("Consolas", 8))
        self.cv_plot.create_text(40, y_etapa_1, text="1", fill="#666", font=("Consolas", 8))
        self.cv_plot.create_text(10, (y_etapa_0 + y_etapa_1)/2, text="ETAPA", fill="white", anchor="w", font=("Arial", 8, "bold"))

        # Para a Saída (Q)
        self.cv_plot.create_line(50, y_saida_0, 700, y_saida_0, fill="#222", dash=(4, 4)) # Nível 0
        self.cv_plot.create_line(50, y_saida_1, 700, y_saida_1, fill="#222", dash=(4, 4)) # Nível 1
        self.cv_plot.create_text(40, y_saida_0, text="0", fill="#666", font=("Consolas", 8))
        self.cv_plot.create_text(40, y_saida_1, text="1", fill="#666", font=("Consolas", 8))
        self.cv_plot.create_text(10, (y_saida_0 + y_saida_1)/2, text="SAÍDA Q", fill="#00ff00", anchor="w", font=("Arial", 8, "bold"))

        # Desenhar os sinais sobre a grelha
        for i in range(len(self.hist_etapa)-1):
            px1, px2 = 50 + (i*6.5), 50 + ((i+1)*6.5) # Offset de 50 para não bater no texto
            
            # Cálculo de Y baseado no histórico (Etapa)
            val_y1_e = y_etapa_0 if self.hist_etapa[i] == 0 else y_etapa_1
            val_y2_e = y_etapa_0 if self.hist_etapa[i+1] == 0 else y_etapa_1
            # Desenhar linha horizontal e a subida/descida vertical
            self.cv_plot.create_line(px1, val_y1_e, px2, val_y1_e, fill="white", width=2)
            if val_y1_e != val_y2_e: # Se houver mudança de estado, desenha linha vertical
                self.cv_plot.create_line(px2, val_y1_e, px2, val_y2_e, fill="white", width=2)
            
            # Cálculo de Y baseado no histórico (Saída)
            val_y1_s = y_saida_0 if self.hist_saida[i] == 0 else y_saida_1
            val_y2_s = y_saida_0 if self.hist_saida[i+1] == 0 else y_saida_1
            self.cv_plot.create_line(px1, val_y1_s, px2, val_y1_s, fill="#00ff00", width=2)
            if val_y1_s != val_y2_s:
                self.cv_plot.create_line(px2, val_y1_s, px2, val_y2_s, fill="#00ff00", width=2)

        self.lbl_timer.config(text=f"TIMER: {t:.1f}s")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorGrafcetCompleto(root)
    root.mainloop()