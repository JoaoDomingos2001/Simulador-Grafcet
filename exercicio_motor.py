import tkinter as tk
from tkinter import messagebox
import math

class GrafcetMotorCyberPro:
    def __init__(self, root):
        self.root = root
        self.root.title("SMC - Sistema de Monitorização de Ciclo (Motor)")
        self.root.geometry("1050x800")
        self.root.configure(bg="#050505")

        # --- ESTADO LÓGICO ---
        self.etapa = 1
        self.botoeira = False
        self.parar = False # Nova entrada %I0.1
        self.motor_ligado = False
        self.angulo = 0
        
        self.setup_ui()
        self.desenhar_grafcet_v3()
        self.loop_processamento()

    def setup_ui(self):
        # Top Bar Estilizada
        top_bar = tk.Frame(self.root, bg="#0a0a0a", height=60, bd=0, highlightthickness=1, highlightbackground="#1a1a1a")
        top_bar.pack(fill="x", side="top")
        
        tk.Label(top_bar, text="SYSTEM STATUS: OPERATIONAL", bg="#0a0a0a", fg="#00ff00", 
                 font=("Orbitron", 10)).pack(side="left", padx=20)
        
        self.lbl_clock = tk.Label(top_bar, text="PLC SCAN: 20ms", bg="#0a0a0a", fg="#444", font=("Consolas", 9))
        self.lbl_clock.pack(side="right", padx=20)

        # Main Layout
        self.content = tk.Frame(self.root, bg="#050505")
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Painel de Animação (Esquerda)
        self.canvas_sim = tk.Canvas(self.content, width=450, height=500, bg="#080808", 
                                    highlightthickness=2, highlightbackground="#111")
        self.canvas_sim.grid(row=0, column=0, padx=10)

        # 2. Painel Grafcet (Direita)
        self.canvas_graf = tk.Canvas(self.content, width=500, height=550, bg="#050505", highlightthickness=0)
        self.canvas_graf.grid(row=0, column=1, padx=20)

        # 3. Consola de Comando (Baixo)
        self.console = tk.Frame(self.root, bg="#0a0a0a", height=150, highlightthickness=1, highlightbackground="#1a1a1a")
        self.console.pack(fill="x", side="bottom")

        # Botão START (Botoeira)
        self.btn_run = tk.Button(self.console, text="START / BOTOEIRA", bg="#003300", fg="#00ff00", 
                                font=("Arial", 10, "bold"), width=20, height=2, relief="flat", activebackground="#004400")
        self.btn_run.pack(side="left", padx=40)
        self.btn_run.bind("<ButtonPress-1>", lambda e: self.set_input("bot", True))
        self.btn_run.bind("<ButtonRelease-1>", lambda e: self.set_input("bot", False))

        # Botão STOP (Novo)
        self.btn_stop = tk.Button(self.console, text="STOP (PARAR)", bg="#330000", fg="#ff4444", 
                                 font=("Arial", 10, "bold"), width=20, height=2, relief="flat", activebackground="#440000")
        self.btn_stop.pack(side="left", padx=10)
        self.btn_stop.bind("<ButtonPress-1>", lambda e: self.set_input("stop", True))
        self.btn_stop.bind("<ButtonRelease-1>", lambda e: self.set_input("stop", False))

        # Monitor de I/O Digital
        self.lbl_io = tk.Label(self.console, text="", bg="#0a0a0a", fg="#00ff00", font=("Consolas", 10), justify="left")
        self.lbl_io.pack(side="right", padx=40)

    def desenhar_grafcet_v3(self):
        self.ui = {}
        x = 120
        y_coords = [60, 200, 340]
        
        # Desenhar Caminhos de Dados
        self.ui['path1'] = self.canvas_graf.create_line(x, 100, x, 200, fill="#111", width=3)
        self.ui['path2'] = self.canvas_graf.create_line(x, 240, x, 340, fill="#111", width=3)
        
        # Linha de Retorno Neon
        self.canvas_graf.create_line(x, 380, x, 420, 40, 420, 40, 150, x, 150, fill="#111", width=2, arrow=tk.LAST)

        etapas_info = {1: "OFF_MODE", 2: "DRIVE_ON", 3: "STANDBY"}
        trans_labels = ["BOTOEIRA=ON", "BOTOEIRA=OFF", "BOTOEIRA=ON"]

        for i, y in enumerate(y_coords, 1):
            # Efeito Glow
            glow = self.canvas_graf.create_rectangle(x-25, y-5, x+25, y+45, fill="#050505", outline="")
            
            # Caixa da Etapa (Estilo Futurista)
            rect = self.canvas_graf.create_rectangle(x-22, y, x+22, y+40, outline="#222", width=2)
            num = self.canvas_graf.create_text(x, y+20, text=str(i), fill="#333", font=("Orbitron", 10, "bold"))
            
            # Ação Lateral
            self.canvas_graf.create_line(x+22, y+20, x+60, y+20, fill="#111")
            a_rect = self.canvas_graf.create_rectangle(x+60, y+8, x+220, y+32, outline="#111", fill="#080808")
            a_txt = self.canvas_graf.create_text(x+140, y+20, text=etapas_info[i], fill="#222", font=("Consolas", 9))
            
            self.ui[f'etapa_{i}'] = {'rect': rect, 'glow': glow, 'num': num, 'atxt': a_txt, 'abox': a_rect}

            # Transições
            if i <= 3:
                ty = y + 80 if i < 3 else 270 # A terceira transição no retorno
                tx = x if i < 3 else 40
                t_line = self.canvas_graf.create_line(tx-15, ty, tx+15, ty, fill="#222", width=4)
                t_lbl = self.canvas_graf.create_text(tx+20, ty, text=trans_labels[i-1], fill="#222", anchor="w", font=("Consolas", 8))
                self.ui[f'trans_{i}'] = {'line': t_line, 'label': t_lbl}

    def loop_processamento(self):
        # Lógica Grafcet
        if self.etapa == 1 and self.botoeira: 
            self.etapa = 2
        elif self.etapa == 2 and (not self.botoeira or self.parar): 
            self.etapa = 3
        elif self.etapa == 3 and self.botoeira: 
            self.etapa = 2

        # Reset para Etapa 1 se STOP for premido fora do ciclo normal (Lógica de segurança)
        if self.parar: self.etapa = 1

        self.motor_ligado = (self.etapa == 2)
        if self.motor_ligado: self.angulo = (self.angulo + 25) % 360

        self.atualizar_visual()
        self.root.after(20, self.loop_processamento)

    def atualizar_visual(self):
        # Atualizar Grafcet
        for i in range(1, 4):
            e = self.ui[f'etapa_{i}']
            is_active = (self.etapa == i)
            cor = "#00ff00" if is_active else "#222"
            glow_cor = "#001a00" if is_active else "#050505"
            
            self.canvas_graf.itemconfig(e['rect'], outline=cor, width=2 if is_active else 1)
            self.canvas_graf.itemconfig(e['glow'], fill=glow_cor)
            self.canvas_graf.itemconfig(e['num'], fill="white" if is_active else "#333")
            self.canvas_graf.itemconfig(e['atxt'], fill=cor)
            self.canvas_graf.itemconfig(e['abox'], outline=cor)

        # Atualizar Transições
        conds = [self.botoeira, not self.botoeira, self.botoeira]
        for i in range(1, 4):
            t = self.ui[f'trans_{i}']
            c = "#00ff00" if conds[i-1] else "#222"
            self.canvas_graf.itemconfig(t['line'], fill=c)
            self.canvas_graf.itemconfig(t['label'], fill=c)

        # Atualizar Motor
        self.canvas_sim.delete("m")
        cx, cy = 225, 250
        # Efeito de rotação
        for i in range(3):
            rad = math.radians(self.angulo + (i * 120))
            self.canvas_sim.create_line(cx, cy, cx+80*math.cos(rad), cy+80*math.sin(rad), 
                                        width=8, fill="#00ff00" if self.motor_ligado else "#111", tags="m")
        self.canvas_sim.create_oval(cx-20, cy-20, cx+20, cy+20, fill="#0a0a0a", outline="#333", tags="m")

        # Monitor de Dados
        io_data = f" INPUT_REGISTER:\n %I0.0 (START): {int(self.botoeira)}\n %I0.1 (STOP):  {int(self.parar)}\n\n OUTPUT_REGISTER:\n %Q0.0 (MOTOR): {int(self.motor_ligado)}"
        self.lbl_io.config(text=io_data)

    def set_input(self, tipo, val):
        if tipo == "bot": self.botoeira = val
        if tipo == "stop": self.parar = val

if __name__ == "__main__":
    root = tk.Tk()
    app = GrafcetMotorCyberPro(root)
    root.mainloop()