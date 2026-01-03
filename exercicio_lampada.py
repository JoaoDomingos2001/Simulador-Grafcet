import tkinter as tk
from tkinter import messagebox

class SimuladorLampadaGrafcet:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Grafcet: Controle de Lâmpada")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a1a")

        # --- ESTADO LÓGICO ---
        self.etapa = 0
        self.CH = False  # Chave (Entrada %I0.0)
        self.lampada_acesa = False # Saída (%Q0.0)
        
        self.setup_ui()
        self.desenhar_grafcet_visual()
        self.ciclo_logico()

    def setup_ui(self):
        # Frame Principal
        self.main_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Área da Lâmpada (Simulação)
        self.canvas_sim = tk.Canvas(self.main_frame, width=400, height=400, bg="white", relief="ridge", bd=2)
        self.canvas_sim.grid(row=0, column=0, padx=10)

        # 2. Área do Grafcet
        self.canvas_graf = tk.Canvas(self.main_frame, width=400, height=400, bg="#1a1a1a", highlightthickness=0)
        self.canvas_graf.grid(row=0, column=1, padx=10)

        # 3. Painel de Monitorização e Controles
        self.panel = tk.Frame(self.root, bg="#333", pady=20)
        self.panel.pack(fill="x", side="bottom")

        # Botão que simula a Chave Física
        self.btn_ch = tk.Button(self.panel, text="ACIONAR CHAVE (CH)", bg="#3498db", fg="white", 
                                font=("Arial", 12, "bold"), width=20)
        self.btn_ch.pack(side="left", padx=50)
        
        # Eventos para simular botão de pressão (clica e segura / solta)
        self.btn_ch.bind("<ButtonPress-1>", self.pressionar_chave)
        self.btn_ch.bind("<ButtonRelease-1>", self.soltar_chave)

        # Monitor de I/O
        self.lbl_io = tk.Label(self.panel, text="", bg="#333", fg="#00ff00", font=("Courier", 11), justify="left")
        self.lbl_io.pack(side="right", padx=50)

    def desenhar_grafcet_visual(self):
        self.ui_etapas = {}
        self.ui_trans = {}
        
        etapas_data = {
            0: ("verificação chave", None),
            1: (None, "S | Liga lâmpada"),
            2: ("verificação chave", None),
            3: (None, "S | Desliga lâmpada")
        }
        labels_trans = ["CH", "¬CH", "CH", "¬CH"]

        for i in range(4):
            y = 40 + (i * 80)
            
            # Etapa (Quadrado Duplo na 0)
            if i == 0:
                self.canvas_graf.create_rectangle(77, y-3, 123, y+43, outline="white")
            rect = self.canvas_graf.create_rectangle(80, y, 120, y+40, outline="white", width=2)
            self.canvas_graf.create_text(100, y+20, text=str(i), fill="white", font=("Arial", 10, "bold"))
            self.ui_etapas[i] = rect

            # Textos e Ações
            txt_info, acao = etapas_data[i]
            if txt_info:
                self.canvas_graf.create_text(130, y+20, text=txt_info, fill="gray", anchor="w")
            if acao:
                self.canvas_graf.create_line(120, y+20, 150, y+20, fill="white")
                self.canvas_graf.create_rectangle(150, y+10, 350, y+30, outline="white")
                self.canvas_graf.create_text(250, y+20, text=acao, fill="white", font=("Arial", 8))

            # Transições
            if i < 4:
                ty = y + 60
                if i < 3: self.canvas_graf.create_line(100, y+40, 100, y+120, fill="white")
                
                self.canvas_graf.create_line(85, ty, 115, ty, fill="white", width=3)
                t_txt = self.canvas_graf.create_text(125, ty, text=labels_trans[i], fill="yellow", anchor="w", font=("Arial", 10, "bold"))
                self.ui_trans[i] = t_txt

        # Linha de Retorno
        self.canvas_graf.create_line(100, 360, 100, 390, 40, 390, 40, 20, 100, 20, 100, 40, fill="white")

    def ciclo_logico(self):
        # Lógica de Transição de Etapas
        if self.etapa == 0 and self.CH:
            self.etapa = 1
        elif self.etapa == 1 and not self.CH:
            self.etapa = 2
        elif self.etapa == 2 and self.CH:
            self.etapa = 3
        elif self.etapa == 3 and not self.CH:
            self.etapa = 0

        # Lógica de Saída (Atuador)
        # Na etapa 1 e 2 a lâmpada deve estar ligada
        if self.etapa in [1, 2]:
            self.lampada_acesa = True
        else:
            self.lampada_acesa = False

        self.atualizar_visual()
        self.root.after(50, self.ciclo_logico)

    def atualizar_visual(self):
        # 1. Simulação da Lâmpada
        self.canvas_sim.delete("all")
        cor_luz = "#f1c40f" if self.lampada_acesa else "#333"
        cor_vidro = "#f7dc6f" if self.lampada_acesa else "#bdc3c7"
        
        # Brilho (se acesa)
        if self.lampada_acesa:
            self.canvas_sim.create_oval(100, 50, 300, 250, fill="#fef9e7", outline="")
            
        # Lâmpada (Desenho simples)
        self.canvas_sim.create_oval(140, 80, 260, 220, fill=cor_vidro, outline="black", width=2)
        self.canvas_sim.create_rectangle(170, 220, 230, 270, fill="gray") # Base
        self.canvas_sim.create_text(200, 320, text="ESTADO: " + ("LIGADA" if self.lampada_acesa else "DESLIGADA"), 
                                    font=("Arial", 12, "bold"))

        # 2. Atualizar Cores do Grafcet
        for i, rect in self.ui_etapas.items():
            self.canvas_graf.itemconfig(rect, fill="#00ff00" if self.etapa == i else "#1a1a1a")

        # Receptividades
        condicoes = [self.CH, not self.CH, self.CH, not self.CH]
        for i, t_txt in self.ui_trans.items():
            self.canvas_graf.itemconfig(t_txt, fill="#00ff00" if condicoes[i] else "yellow")

        # 3. Monitor de I/O
        io_text = f"ENTRADAS:\n%I0.0 (CH): {1 if self.CH else 0}\n\nSAÍDAS:\n%Q0.0 (LÂMP): {1 if self.lampada_acesa else 0}"
        self.lbl_io.config(text=io_text)

    def pressionar_chave(self, event):
        self.CH = True

    def soltar_chave(self, event):
        self.CH = False

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorLampadaGrafcet(root)
    root.mainloop()