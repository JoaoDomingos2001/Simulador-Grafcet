import tkinter as tk
from tkinter import ttk
import time
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =============================================================================
# MÓDULO 1: GRAFCET ULTIMATE (Lógica Complexa: OU, E, SALTO, INC)
# =============================================================================
class GrafcetUltimateView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1a1a1a")
        self.modo = "OU" 
        self.etapas = {i: False for i in range(15)}
        self.etapas[0] = True
        self.entradas = {"A": False, "B": False}
        self.timers = {i: 0 for i in range(15)} 
        
        self.setup_ui()
        self.active = True
        self.ciclo_logico()

    def setup_ui(self):
        # Menu Superior
        menu = tk.Frame(self, bg="#333", pady=5)
        menu.pack(fill="x")
        
        btns = [("Divergência OU", "OU"), ("Divergência E", "E"), 
                ("Salto/Repetição", "SALTO"), ("Incondicional", "INC")]
        for texto, m in btns:
            tk.Button(menu, text=texto, command=lambda v=m: self.mudar_modo(v), 
                      bg="#444", fg="white", width=15).pack(side="left", padx=5)

        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Painel Controle
        painel = tk.Frame(self, bg="#222", pady=10)
        painel.pack(fill="x", side="bottom")
        
        self.btn_a = tk.Button(painel, text="Sensor A (0)", width=12, command=lambda: self.toggle("A"))
        self.btn_a.pack(side="left", padx=20)
        self.btn_b = tk.Button(painel, text="Sensor B (0)", width=12, command=lambda: self.toggle("B"))
        self.btn_b.pack(side="left", padx=20)
        
        self.info_lbl = tk.Label(painel, text="Modo: Divergência em OU", bg="#222", fg="yellow")
        self.info_lbl.pack(side="right", padx=20)

    def mudar_modo(self, m):
        self.modo = m
        self.info_lbl.config(text=f"Modo: {m}")
        self.reset_sistema()

    def reset_sistema(self):
        self.etapas = {i: False for i in range(15)}
        self.etapas[0] = True
        self.timers = {i: time.time() for i in range(15)}

    def toggle(self, var):
        self.entradas[var] = not self.entradas[var]
        btn = self.btn_a if var == "A" else self.btn_b
        btn.config(text=f"Sensor {var} ({int(self.entradas[var])})", 
                   bg="#2e7d32" if self.entradas[var] else "#444")

    def verificar_tempo(self, etapa, segundos):
        if not self.etapas[etapa]:
            self.timers[etapa] = time.time()
            return False
        return (time.time() - self.timers[etapa]) >= segundos

    def ciclo_logico(self):
        if not self.winfo_exists(): return # Para se a janela fechar
        
        a, b = self.entradas["A"], self.entradas["B"]
        
        if self.modo == "OU":
            if self.etapas[0] and a: self.etapas[0], self.etapas[1] = False, True
            elif self.etapas[0] and b: self.etapas[0], self.etapas[2] = False, True
            if self.etapas[1] and self.verificar_tempo(1, 3): self.etapas[1], self.etapas[3] = False, True
            if self.etapas[2] and a: self.etapas[2], self.etapas[4] = False, True
            if (self.etapas[3] and b) or (self.etapas[4] and b):
                self.etapas[3] = self.etapas[4] = False
                self.etapas[5] = True

        elif self.modo == "E":
            if self.etapas[0] and a: self.etapas[0], self.etapas[1], self.etapas[2] = False, True, True
            if self.etapas[1] and b: self.etapas[1], self.etapas[3] = False, True
            if self.etapas[2] and self.verificar_tempo(2, 4): self.etapas[2], self.etapas[4] = False, True
            if self.etapas[3] and self.etapas[4] and a:
                self.etapas[3] = self.etapas[4] = False
                self.etapas[5] = True

        elif self.modo == "SALTO":
            if self.etapas[0] and a: self.etapas[0], self.etapas[2] = False, True 
            elif self.etapas[0] and b: self.etapas[0], self.etapas[1] = False, True 
            if self.etapas[1] and a: self.etapas[1], self.etapas[2] = False, True 
            if self.etapas[2] and b: self.etapas[2], self.etapas[0] = False, True 

        elif self.modo == "INC":
            if self.etapas[0] and a: self.etapas[0], self.etapas[1] = False, True
            if self.etapas[1] and self.verificar_tempo(1, 2): 
                self.etapas[1], self.etapas[2] = False, True

        self.desenhar()
        self.after(50, self.ciclo_logico)

    def draw_step(self, x, y, id):
        cor = "#00e676" if self.etapas[id] else "#555"
        self.canvas.create_rectangle(x-30, y-20, x+30, y+20, outline=cor, width=3, fill="#333")
        self.canvas.create_text(x, y, text=f"E{id}", fill="white", font=("Arial", 10, "bold"))
        if self.etapas[id]:
            decorrido = time.time() - self.timers[id]
            self.canvas.create_text(x, y+35, text=f"{decorrido:.1f}s", fill="cyan")

    def draw_trans(self, x, y, cond):
        self.canvas.create_line(x, y-20, x, y+20, fill="white", width=2)
        self.canvas.create_line(x-15, y, x+15, y, fill="red", width=3)
        self.canvas.create_text(x+25, y, text=cond, fill="red", anchor="w", font=("Arial", 9, "bold"))

    def desenhar(self):
        self.canvas.delete("all")
        xm = 500 # Centralizado na visualização maior
        
        # Copiado a lógica de desenho do GrafcetUltimate original
        if self.modo == "OU":
            self.draw_step(xm, 50, 0)
            self.canvas.create_line(xm, 70, xm, 100, fill="white", width=2)
            self.canvas.create_line(xm-150, 100, xm+150, 100, fill="white", width=2)
            for offset, st_id, trans_init, trans_mid, st_id2 in [(-150, 1, "A", "T/E1/3s", 3), (150, 2, "B", "A", 4)]:
                self.canvas.create_line(xm+offset, 100, xm+offset, 120, fill="white", width=2)
                self.draw_trans(xm+offset, 130, trans_init)
                self.draw_step(xm+offset, 170, st_id)
                self.draw_trans(xm+offset, 220, trans_mid)
                self.draw_step(xm+offset, 260, st_id2)
                self.canvas.create_line(xm+offset, 280, xm+offset, 310, fill="white", width=2)
            self.canvas.create_line(xm-150, 310, xm+150, 310, fill="white", width=2)
            self.draw_trans(xm, 340, "B")
            self.draw_step(xm, 380, 5)

        elif self.modo == "E":
            self.draw_step(xm, 50, 0)
            self.draw_trans(xm, 90, "A")
            self.canvas.create_line(xm-150, 110, xm+150, 110, fill="white", width=4)
            self.canvas.create_line(xm-150, 116, xm+150, 116, fill="white", width=4)
            for offset, st1, trans, st2 in [(-150, 1, "B", 3), (150, 2, "T/E2/4s", 4)]:
                self.canvas.create_line(xm+offset, 116, xm+offset, 140, fill="white", width=2)
                self.draw_step(xm+offset, 160, st1)
                self.draw_trans(xm+offset, 210, trans)
                self.draw_step(xm+offset, 250, st2)
                self.canvas.create_line(xm+offset, 270, xm+offset, 290, fill="white", width=2)
            self.canvas.create_line(xm-150, 290, xm+150, 290, fill="white", width=4)
            self.canvas.create_line(xm-150, 296, xm+150, 296, fill="white", width=4)
            self.draw_trans(xm, 325, "A")
            self.draw_step(xm, 365, 5)

        elif self.modo == "SALTO":
            self.draw_step(xm, 50, 0)
            self.canvas.create_line(xm, 70, xm, 90, fill="white", width=2)
            self.canvas.create_line(xm, 90, xm+100, 90, fill="white", width=2)
            self.draw_trans(xm+100, 110, "A (Salto)")
            self.canvas.create_line(xm+100, 130, xm+100, 280, fill="white", width=2)
            self.canvas.create_line(xm+100, 280, xm, 280, fill="white", width=2, arrow=tk.LAST)
            self.draw_trans(xm, 110, "B")
            self.draw_step(xm, 150, 1)
            self.draw_trans(xm, 200, "A")
            self.draw_step(xm, 240, 2)
            self.canvas.create_line(xm, 260, xm, 310, fill="white", width=2)
            self.canvas.create_line(xm, 310, xm-100, 310, fill="white", width=2)
            self.canvas.create_line(xm-100, 310, xm-100, 50, fill="white", width=2)
            self.canvas.create_line(xm-100, 50, xm-30, 50, fill="white", width=2, arrow=tk.LAST)
            self.draw_trans(xm-100, 180, "B (Loop)")

        elif self.modo == "INC":
            self.draw_step(xm, 50, 0)
            self.draw_trans(xm, 100, "A")
            self.draw_step(xm, 150, 1)
            self.draw_trans(xm, 200, "1 (Auto)")
            self.draw_step(xm, 250, 2)
            self.canvas.create_line(xm, 270, xm, 300, fill="white", width=2)


# =============================================================================
# MÓDULO 2: IEC 61131 DETALHADO (Matplotlib)
# =============================================================================
class IEC61131View(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.tempos = [0]
        self.dados_x15 = [0]
        self.dados_x16 = [0]
        self.inicio_simulacao = None
        self.etapa_ativa = 0 
        self.rodando = False
        
        self.setup_ui()

    def setup_ui(self):
        # Esquema
        self.canvas_sfc = tk.Canvas(self, width=600, height=180, bg="white", highlightthickness=0)
        self.canvas_sfc.pack(pady=10)
        
        self.rect15 = self.canvas_sfc.create_rectangle(250, 20, 350, 60, width=2)
        self.canvas_sfc.create_text(300, 40, text="15: Aciona M1", font=("Arial", 10, "bold"))
        self.canvas_sfc.create_line(300, 60, 300, 110, width=2)
        self.trans_line = self.canvas_sfc.create_line(280, 85, 320, 85, width=4)
        self.canvas_sfc.create_text(370, 85, text="5s / X15", fill="red", font=("Arial", 10, "italic"))
        self.rect16 = self.canvas_sfc.create_rectangle(250, 110, 350, 150, width=2)
        self.canvas_sfc.create_text(300, 130, text="16: Aciona V1", font=("Arial", 10, "bold"))

        # Gráficos
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 4), sharex=True)
        self.fig.subplots_adjust(hspace=0.3)
        self.ax1.set_ylabel("X15 (Motor)", fontsize=9)
        self.line15, = self.ax1.step(self.tempos, self.dados_x15, where='post', color='green', linewidth=2)
        self.ax2.set_ylabel("X16 (Válvula)", fontsize=9)
        self.line16, = self.ax2.step(self.tempos, self.dados_x16, where='post', color='blue', linewidth=2)
        self.ax1.grid(True, linestyle='--', alpha=0.5); self.ax2.grid(True, linestyle='--', alpha=0.5)

        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20)

        # Botões
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="EXECUTAR CICLO", command=self.iniciar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="RESET", command=self.reset).pack(side=tk.LEFT, padx=10)

    def iniciar(self):
        if not self.rodando:
            self.reset()
            self.etapa_ativa = 15
            self.rodando = True
            self.inicio_simulacao = time.time()
            self.atualizar()

    def reset(self):
        self.rodando = False
        self.etapa_ativa = 0
        self.tempos = [0]
        self.dados_x15 = [0]
        self.dados_x16 = [0]
        self.canvas_sfc.itemconfig(self.rect15, fill="white")
        self.canvas_sfc.itemconfig(self.rect16, fill="white")
        self.atualizar_graficos()

    def atualizar_graficos(self):
        self.line15.set_data(self.tempos, self.dados_x15)
        self.line16.set_data(self.tempos, self.dados_x16)
        tempo_max = max(8, self.tempos[-1])
        self.ax1.set_xlim(0, tempo_max); self.ax1.set_ylim(-0.1, 1.1)
        self.ax2.set_xlim(0, tempo_max); self.ax2.set_ylim(-0.1, 1.1)
        self.plot_canvas.draw()

    def atualizar(self):
        if not self.rodando or not self.winfo_exists(): return
        t_atual = time.time() - self.inicio_simulacao
        self.tempos.append(t_atual)

        if self.etapa_ativa == 15:
            self.canvas_sfc.itemconfig(self.rect15, fill="#90EE90")
            self.dados_x15.append(1); self.dados_x16.append(0)
            if t_atual >= 5.0: 
                self.etapa_ativa = 16
                self.canvas_sfc.itemconfig(self.rect15, fill="white")
        elif self.etapa_ativa == 16:
            self.canvas_sfc.itemconfig(self.rect16, fill="#90EE90")
            self.dados_x15.append(0); self.dados_x16.append(1)
            if t_atual >= 8.0: self.rodando = False
        
        self.atualizar_graficos()
        self.after(50, self.atualizar)


# =============================================================================
# MÓDULO 3: RECEPTIVIDADE (Portado de Pygame para Tkinter)
# =============================================================================
class ReceptividadeView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f5f5f5")
        self.step_15 = 1
        self.step_16 = 0
        self.B1 = 0
        self.B2 = 0
        
        # Histórico
        self.hist_size = 200
        self.history = { '15': deque([1]*self.hist_size, self.hist_size), 
                         '16': deque([0]*self.hist_size, self.hist_size),
                         'B1': deque([0]*self.hist_size, self.hist_size), 
                         'B2': deque([0]*self.hist_size, self.hist_size) }

        self.setup_ui()
        self.ciclo_logico()

    def setup_ui(self):
        # Área Principal
        self.canvas = tk.Canvas(self, bg="#f5f5f5", width=900, height=400)
        self.canvas.pack(pady=10)

        # Botões
        ctrl_frame = tk.Frame(self, bg="#f5f5f5")
        ctrl_frame.pack(pady=10)
        
        self.btn_b1 = tk.Button(ctrl_frame, text="B1: 0", command=lambda: self.toggle('B1'), bg="#3498db", fg="white", width=10)
        self.btn_b1.pack(side="left", padx=10)
        
        self.btn_b2 = tk.Button(ctrl_frame, text="B2: 0", command=lambda: self.toggle('B2'), bg="#e74c3c", fg="white", width=10)
        self.btn_b2.pack(side="left", padx=10)
        
        tk.Button(ctrl_frame, text="Reset", command=self.reset).pack(side="left", padx=20)

    def toggle(self, var):
        if var == 'B1': self.B1 = 1 - self.B1
        else: self.B2 = 1 - self.B2
        self.update_btns()

    def update_btns(self):
        self.btn_b1.config(text=f"B1: {self.B1}")
        self.btn_b2.config(text=f"B2: {self.B2}")

    def reset(self):
        self.step_15, self.step_16 = 1, 0
        self.B1, self.B2 = 0, 0
        self.update_btns()

    def ciclo_logico(self):
        if not self.winfo_exists(): return
        
        # Lógica
        receptivity = (self.B1 == 1 and self.B2 == 0)
        if self.step_15 and receptivity:
            self.step_15 = 0
            self.step_16 = 1

        # Atualiza histórico
        self.history['15'].append(self.step_15)
        self.history['16'].append(self.step_16)
        self.history['B1'].append(self.B1)
        self.history['B2'].append(self.B2)
        
        self.desenhar()
        self.after(50, self.ciclo_logico)

    def desenhar(self):
        self.canvas.delete("all")
        
        # --- Desenho do GRAFCET (Esquerda) ---
        # Etapa 15
        self.canvas.create_rectangle(100, 50, 160, 110, width=2)
        self.canvas.create_text(130, 80, text="15", font=("Arial", 12, "bold"))
        if self.step_15: self.canvas.create_oval(140, 90, 155, 105, fill="#2ecc71")
        
        # Transição
        self.canvas.create_line(130, 110, 130, 200, width=2)
        self.canvas.create_line(110, 155, 150, 155, width=4) # Traço transição
        
        # Texto Lógica
        cond_color = "#2ecc71" if (self.B1 and not self.B2) else "#e74c3c"
        self.canvas.create_text(170, 155, text="B1=ON e B2=OFF", fill=cond_color, anchor="w", font=("Arial", 10, "bold"))
        
        # Etapa 16
        self.canvas.create_rectangle(100, 200, 160, 260, width=2)
        self.canvas.create_text(130, 230, text="16", font=("Arial", 12, "bold"))
        if self.step_16: self.canvas.create_oval(140, 240, 155, 255, fill="#2ecc71")

        # --- Desenho dos GRÁFICOS (Direita) ---
        start_x, width = 350, 500
        plots = [("Etapa 15", '15', 50, "#2ecc71"), ("B1", 'B1', 150, "#3498db"),
                 ("B2", 'B2', 250, "#e74c3c"), ("Etapa 16", '16', 350, "black")]
        
        for name, key, y_base, color in plots:
            self.canvas.create_text(start_x, y_base-20, text=name, anchor="w", font=("Arial", 10, "bold"))
            self.canvas.create_line(start_x, y_base+40, start_x+width, y_base+40, fill="#ccc") # Eixo
            
            pts = []
            data = list(self.history[key])
            for i, val in enumerate(data):
                px = start_x + (i * (width/self.hist_size))
                py = (y_base+40) - (val * 30)
                pts.append(px)
                pts.append(py)
            if len(pts) > 2:
                self.canvas.create_line(pts, fill=color, width=2)


# =============================================================================
# MÓDULO 4: TRANSIÇÃO SIMPLES (Portado de Pygame para Tkinter)
# =============================================================================
class TransicaoSimplesView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f5f5f5")
        self.step_15 = 1
        self.step_16 = 0
        self.trans_a = 0
        self.history_15 = deque([1]*200, maxlen=200)
        self.history_a = deque([0]*200, maxlen=200)
        self.history_16 = deque([0]*200, maxlen=200)
        
        self.setup_ui()
        self.ciclo()

    def setup_ui(self):
        self.canvas = tk.Canvas(self, bg="#f5f5f5", width=900, height=400)
        self.canvas.pack(pady=10)
        
        f = tk.Frame(self)
        f.pack()
        self.btn_a = tk.Button(f, text="Alternar 'a'", command=self.toggle_a, bg="#3498db", fg="white")
        self.btn_a.pack(side="left", padx=10)
        tk.Button(f, text="Reset", command=self.reset).pack(side="left")

    def toggle_a(self):
        self.trans_a = 1 if self.trans_a == 0 else 0

    def reset(self):
        self.step_15, self.step_16, self.trans_a = 1, 0, 0

    def ciclo(self):
        if not self.winfo_exists(): return
        
        if self.step_15 and self.trans_a:
            self.step_15 = 0
            self.step_16 = 1
            
        self.history_15.append(self.step_15)
        self.history_a.append(self.trans_a)
        self.history_16.append(self.step_16)
        
        self.desenhar()
        self.after(30, self.ciclo)

    def desenhar(self):
        self.canvas.delete("all")
        # Grafcet Simples
        self.canvas.create_rectangle(80, 80, 140, 140, width=2) # 15
        if self.step_15: self.canvas.create_oval(115, 120, 130, 135, fill="green")
        self.canvas.create_text(110, 95, text="15", font=("Arial", 12))
        
        self.canvas.create_line(110, 140, 110, 200)
        self.canvas.create_line(90, 170, 130, 170, width=4) # Transição
        col = "green" if self.trans_a else "red"
        self.canvas.create_text(140, 170, text=f"a={self.trans_a}", fill=col, anchor="w")
        
        self.canvas.create_rectangle(80, 200, 140, 260, width=2) # 16
        if self.step_16: self.canvas.create_oval(115, 240, 130, 255, fill="green")
        self.canvas.create_text(110, 215, text="16", font=("Arial", 12))

        # Gráficos
        start_x, w = 350, 450
        sets = [("Etapa 15", self.history_15, 80, "green"),
                ("Transição 'a'", self.history_a, 200, "blue"),
                ("Etapa 16", self.history_16, 320, "purple")]
        
        for name, data, y, color in sets:
            self.canvas.create_text(start_x, y-20, text=name, anchor="w", font=("Arial", 9, "bold"))
            self.canvas.create_line(start_x, y+50, start_x+w, y+50, fill="#ccc")
            pts = []
            for i, val in enumerate(data):
                pts.append(start_x + (i*(w/200)))
                pts.append((y+50) - (val*40))
            if len(pts)>2: self.canvas.create_line(pts, fill=color, width=2)


# =============================================================================
# APLICAÇÃO PRINCIPAL (LAUNCHER)
# =============================================================================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Super Simulador GRAFCET Integrado")
        self.geometry("1200x850")
        
        # Barra Lateral de Navegação
        sidebar = tk.Frame(self, bg="#2c3e50", width=200)
        sidebar.pack(side="left", fill="y")
        
        ttk.Label(sidebar, text="MÓDULOS", background="#2c3e50", foreground="white", 
                  font=("Arial", 14, "bold")).pack(pady=20)

        nav_btns = [
            ("Grafcet Ultimate", GrafcetUltimateView),
            ("Timing IEC 61131", IEC61131View),
            ("Receptividade/Bordas", ReceptividadeView),
            ("Transição Simples", TransicaoSimplesView)
        ]

        for txt, view_class in nav_btns:
            b = tk.Button(sidebar, text=txt, bg="#34495e", fg="white", 
                          relief="flat", pady=10, width=20,
                          command=lambda v=view_class: self.show_view(v))
            b.pack(pady=5, padx=10)

        # Container Principal
        self.container = tk.Frame(self, bg="white")
        self.container.pack(side="right", fill="both", expand=True)
        
        self.current_view = None
        self.show_view(GrafcetUltimateView) # Inicia com a visão principal

    def show_view(self, view_class):
        if self.current_view:
            # Limpeza necessária para o Matplotlib não vazar memória
            if hasattr(self.current_view, 'rodando'): 
                self.current_view.rodando = False
            self.current_view.destroy()
        
        self.current_view = view_class(self.container)
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()