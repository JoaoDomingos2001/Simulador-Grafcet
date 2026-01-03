import tkinter as tk
from tkinter import messagebox

class FuradeiraGrafcetIO:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Grafcet com Monitor de I/O")
        self.root.geometry("1200x750")
        self.root.configure(bg="#1a1a1a")

        # --- ESTADO LÓGICO ---
        self.etapa = 0
        self.furadeira_y = 50
        self.contagem = 0
        self.em_execucao = False
        self.emergencia = False
        self.caixa_perfurada = False
        
        # Mapeamento de I/O
        self.inputs = {"M": 0, "b1": 0, "b2": 0, "h": 1}
        self.outputs = {"Motor": 0, "V_Alta": 0, "V_Baixa": 0, "Recuo": 0}

        self.setup_ui()
        self.desenhar_grafcet_estatico()
        self.atualizar_ciclo()

    def setup_ui(self):
        # Frame Principal com 3 colunas
        self.main_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Coluna Simulação
        self.canvas_sim = tk.Canvas(self.main_frame, width=380, height=450, bg="white", highlightthickness=1)
        self.canvas_sim.grid(row=0, column=0, padx=5)

        # 2. Coluna Grafcet
        self.canvas_graf = tk.Canvas(self.main_frame, width=420, height=450, bg="#1a1a1a", highlightthickness=0)
        self.canvas_graf.grid(row=0, column=1, padx=5)

        # 3. Coluna Monitor de I/O (NOVO)
        self.frame_io = tk.LabelFrame(self.main_frame, text=" MONITOR DE I/O (PLC) ", bg="#1a1a1a", fg="white", font=("Arial", 10, "bold"))
        self.frame_io.grid(row=0, column=2, sticky="ns", padx=5)
        
        self.lbl_io_in = tk.Label(self.frame_io, text="", justify="left", bg="#1a1a1a", fg="#00ff00", font=("Courier", 11))
        self.lbl_io_in.pack(pady=10, padx=10)
        
        self.lbl_io_out = tk.Label(self.frame_io, text="", justify="left", bg="#1a1a1a", fg="#00ffff", font=("Courier", 11))
        self.lbl_io_out.pack(pady=10, padx=10)

        # Painel Inferior
        self.panel = tk.Frame(self.root, bg="#333", pady=15)
        self.panel.pack(fill="x", side="bottom")

        tk.Button(self.panel, text="START (M)", bg="#2ecc71", fg="white", font=("Arial", 11, "bold"), width=12, command=self.clique_start).pack(side="left", padx=50)
        tk.Button(self.panel, text="STOP", bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), width=12, command=self.clique_emergencia).pack(side="right", padx=50)
        
        self.lbl_status = tk.Label(self.root, text="PRONTO", bg="#1a1a1a", fg="white", font=("Arial", 12))
        self.lbl_status.pack(pady=5)

    def desenhar_grafcet_estatico(self):
        self.ui_etapas = {}
        self.ui_trans = {}
        etapas_info = {
            0: ("Repouso", None),
            1: ("Aproximação", "Q0.0 (Motor) + Q0.1 (V_Alta)"),
            2: ("Furação", "Q0.0 (Motor) + Q0.2 (V_Baixa)"),
            3: ("Retorno", "Q0.3 (V_Recuo Alta)")
        }
        recepts = ["M · h", "b1", "b2", "h"]

        for i in range(4):
            y = 40 + (i * 100)
            rect = self.canvas_graf.create_rectangle(80, y, 120, y+40, outline="white", width=2)
            self.canvas_graf.create_text(100, y+20, text=str(i), fill="white")
            self.ui_etapas[i] = rect
            
            # Blocos de Ação
            if etapas_info[i][1]:
                self.canvas_graf.create_line(120, y+20, 150, y+20, fill="white")
                self.canvas_graf.create_rectangle(150, y+5, 380, y+35, outline="gray")
                self.canvas_graf.create_text(265, y+20, text=etapas_info[i][1], fill="#00ffff", font=("Arial", 7))
            
            # Transições
            if i < 3:
                self.canvas_graf.create_line(100, y+40, 100, y+100, fill="white")
                self.canvas_graf.create_line(85, y+70, 115, y+70, fill="white", width=3)
                self.ui_trans[i] = self.canvas_graf.create_text(130, y+70, text=recepts[i], fill="yellow", anchor="w")
        
        # Linha de volta
        self.ui_trans[3] = self.canvas_graf.create_text(130, 420, text="h", fill="yellow", anchor="w")
        self.canvas_graf.create_line(100, 380, 100, 430, 40, 430, 40, 20, 100, 20, 100, 40, fill="white")

    def atualizar_ciclo(self):
        # 1. Atualizar Sensores (Inputs)
        self.inputs["h"] = 1 if self.furadeira_y <= 55 else 0
        self.inputs["b1"] = 1 if 155 <= self.furadeira_y <= 175 else 0
        self.inputs["b2"] = 1 if self.furadeira_y >= 340 else 0

        # 2. Atualizar Saídas (Outputs) baseadas na Etapa
        self.outputs = {"Motor": 0, "V_Alta": 0, "V_Baixa": 0, "Recuo": 0}
        if self.etapa == 1: self.outputs["Motor"] = 1; self.outputs["V_Alta"] = 1
        elif self.etapa == 2: self.outputs["Motor"] = 1; self.outputs["V_Baixa"] = 1
        elif self.etapa == 3: self.outputs["Recuo"] = 1

        # 3. Lógica de Movimento
        if self.em_execucao:
            if self.emergencia:
                if self.furadeira_y > 50: self.furadeira_y -= 15
                else: self.reset_total()
            else:
                if self.etapa == 1:
                    if not self.inputs["b1"]: self.furadeira_y += 10
                    else: self.etapa = 2
                elif self.etapa == 2:
                    if not self.inputs["b2"]: self.furadeira_y += 2
                    else: self.etapa = 3; self.caixa_perfurada = True
                elif self.etapa == 3:
                    if not self.inputs["h"]: self.furadeira_y -= 12
                    else: self.contagem += 1; self.reset_total()

        self.renderizar_interface()
        self.root.after(40, self.atualizar_ciclo)

    def renderizar_interface(self):
        # Monitor de I/O Texto
        txt_in = " ENTRADAS (%I):\n" + "-"*18 + "\n"
        txt_in += f"%I0.0 (M):    {self.inputs['M']}\n"
        txt_in += f"%I0.1 (h):    {self.inputs['h']}\n"
        txt_in += f"%I0.2 (b1):   {self.inputs['b1']}\n"
        txt_in += f"%I0.3 (b2):   {self.inputs['b2']}"
        self.lbl_io_in.config(text=txt_in)

        txt_out = " SAÍDAS (%Q):\n" + "-"*18 + "\n"
        txt_out += f"%Q0.0 (Mot):   {self.outputs['Motor']}\n"
        txt_out += f"%Q0.1 (V_Alt): {self.outputs['V_Alta']}\n"
        txt_out += f"%Q0.2 (V_Bax): {self.outputs['V_Baixa']}\n"
        txt_out += f"%Q0.3 (Recuo): {self.outputs['Recuo']}"
        self.lbl_io_out.config(text=txt_out)

        # Atualizar Grafcet
        for i, r in self.ui_etapas.items():
            self.canvas_graf.itemconfig(r, fill="#00ff00" if self.etapa == i else "#1a1a1a")

        # Atualizar Simulação
        self.canvas_sim.delete("all")
        self.canvas_sim.create_rectangle(120, 360, 280, 440, fill="#D2B48C") # Caixa
        if self.caixa_perfurada or self.furadeira_y > 340:
            self.canvas_sim.create_oval(190, 355, 210, 365, fill="black")
        
        cor_b = "red" if self.outputs["Motor"] else "black"
        self.canvas_sim.create_rectangle(170, self.furadeira_y, 230, self.furadeira_y+40, fill="#555")
        self.canvas_sim.create_line(200, self.furadeira_y+40, 200, self.furadeira_y+100, width=4, fill=cor_b)

    def clique_start(self):
        if self.etapa == 0 and self.inputs["h"]:
            self.inputs["M"] = 1; self.etapa = 1; self.em_execucao = True; self.emergencia = False

    def clique_emergencia(self):
        if self.em_execucao: self.emergencia = True; self.etapa = 3

    def reset_total(self):
        self.etapa = 0; self.furadeira_y = 50; self.em_execucao = False; self.inputs["M"] = 0; self.caixa_perfurada = False

if __name__ == "__main__":
    root = tk.Tk()
    app = FuradeiraGrafcetIO(root)
    root.mainloop()