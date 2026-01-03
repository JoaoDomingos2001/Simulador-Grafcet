import tkinter as tk
from tkinter import ttk

class GrafcetGruaNormativo:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Grafcet Normativo: Sistema de Carga (Grua)")
        self.root.geometry("1100x800")
        self.root.configure(bg="#1a1a1a")

        # --- ESTADO INTERNO ---
        self.etapa = 0
        self.inputs = {"M": 0, "b": 0, "a": 1}
        self.outputs = {"M1": 0, "M2": 0, "Grua": 0}
        
        # Variáveis de Animação
        self.carro_x = 50
        self.grua_y = 30
        self.caixa_no_carro = False
        self.caixa_na_grua = True
        self.em_execucao = False

        self.setup_ui()
        self.desenhar_grafcet_normativo()
        self.atualizar_loop()

    def setup_ui(self):
        # Frame Principal
        self.main_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. Canvas de Simulação (Topo)
        self.canvas_sim = tk.Canvas(self.main_frame, width=1000, height=300, bg="white", relief="ridge", bd=3)
        self.canvas_sim.grid(row=0, column=0, columnspan=2, pady=10)

        # 2. Canvas do Grafcet (Esquerda)
        self.canvas_graf = tk.Canvas(self.main_frame, width=500, height=450, bg="#1a1a1a", highlightthickness=0)
        self.canvas_graf.grid(row=1, column=0, padx=10)

        # 3. Painel de I/O (Direita)
        self.frame_io = tk.LabelFrame(self.main_frame, text=" ESTADO DO PLC ", bg="#1a1a1a", fg="white", font=("Arial", 10, "bold"))
        self.frame_io.grid(row=1, column=1, sticky="nsew", padx=10)
        
        self.lbl_io = tk.Label(self.frame_io, text="", justify="left", bg="#1a1a1a", fg="#00ff00", font=("Courier", 12))
        self.lbl_io.pack(pady=20, padx=20)

        # Botões de Controle
        self.btn_frame = tk.Frame(self.root, bg="#333", pady=10)
        self.btn_frame.pack(fill="x", side="bottom")

        tk.Button(self.btn_frame, text="START (M)", bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), 
                  width=15, command=self.clique_start).pack(side="left", padx=100)
        
        self.lbl_pecas = tk.Label(self.btn_frame, text="PEÇAS: 0", bg="#333", fg="white", font=("Arial", 12, "bold"))
        self.lbl_pecas.pack(side="right", padx=100)

    def desenhar_grafcet_normativo(self):
        self.ui_etapas = {}
        self.ui_trans = {}
        
        # Definição das Etapas e Ações (Conforme norma Grafcet)
        etapas_info = {
            0: ("Repouso", None),
            1: ("Mov. Dir.", "M1 (Motor Direita)"),
            2: ("Carga", "Atuador Grua (Descer/Subir)"),
            3: ("Mov. Esq.", "M2 (Motor Esquerda)")
        }
        receptividades = ["M · a", "b", "h", "a"] # h é o sensor de grua no topo (simplificado)

        for i in range(4):
            y = 40 + (i * 90)
            
            # Etapa (Quadrado) - Duplo para Etapa 0
            if i == 0:
                self.canvas_graf.create_rectangle(97, y-3, 143, y+43, outline="white")
            rect = self.canvas_graf.create_rectangle(100, y, 140, y+40, outline="white", width=2)
            self.canvas_graf.create_text(120, y+20, text=str(i), fill="white", font=("Arial", 10, "bold"))
            self.ui_etapas[i] = rect

            # Blocos de Ação Laterais
            nome, acao = etapas_info[i]
            if acao:
                self.canvas_graf.create_line(140, y+20, 170, y+20, fill="white")
                self.canvas_graf.create_rectangle(170, y+5, 450, y+35, outline="white")
                self.canvas_graf.create_text(310, y+20, text=acao, fill="#00ffff", font=("Arial", 8))

            # Transições (Traços Horizontais)
            if i < 4:
                ty = y + 65
                if i < 3: self.canvas_graf.create_line(120, y+40, 120, y+130, fill="white")
                
                self.canvas_graf.create_line(105, ty, 135, ty, fill="white", width=3)
                t_txt = self.canvas_graf.create_text(145, ty, text=receptividades[i], fill="yellow", anchor="w", font=("Courier", 11, "bold"))
                self.ui_trans[i] = t_txt

        # Linha de Retorno
        self.canvas_graf.create_line(120, 360, 120, 410, 40, 410, 40, 20, 120, 20, 120, 40, fill="white")

    def atualizar_loop(self):
        # 1. Sensores
        self.inputs["a"] = 1 if self.carro_x <= 55 else 0
        self.inputs["b"] = 1 if self.carro_x >= 540 else 0
        
        # 2. Lógica de Movimento
        if self.em_execucao:
            if self.etapa == 1: # Direita
                if self.carro_x < 550: self.carro_x += 8
                else: self.etapa = 2
            
            elif self.etapa == 2: # Grua
                if self.caixa_na_grua: # Descendo
                    if self.grua_y < 190: self.grua_y += 5
                    else: 
                        self.caixa_na_grua = False
                        self.caixa_no_carro = True
                else: # Subindo
                    if self.grua_y > 30: self.grua_y -= 5
                    else: self.etapa = 3
            
            elif self.etapa == 3: # Esquerda
                if self.carro_x > 50: self.carro_x -= 8
                else: 
                    self.etapa = 0
                    self.em_execucao = False
                    self.inputs["M"] = 0
                    self.caixa_no_carro = False
                    self.caixa_na_grua = True

        self.renderizar_tudo()
        self.root.after(40, self.atualizar_loop)

    def renderizar_tudo(self):
        # Limpar Simulação
        self.canvas_sim.delete("all")
        
        # Desenhar Cenário
        self.canvas_sim.create_rectangle(0, 260, 1000, 280, fill="#555") # Chão
        # Sensores Visuais
        self.canvas_sim.create_oval(50, 285, 70, 305, fill="green" if self.inputs["a"] else "gray")
        self.canvas_sim.create_text(60, 315, text="S_a")
        self.canvas_sim.create_oval(550, 285, 570, 305, fill="green" if self.inputs["b"] else "gray")
        self.canvas_sim.create_text(560, 315, text="S_b")

        # Carrinho
        self.canvas_sim.create_rectangle(self.carro_x, 220, self.carro_x+80, 260, fill="#0055ff", width=2)
        
        # Grua e Caixa
        self.canvas_sim.create_line(560, 0, 560, self.grua_y, width=4, fill="#777")
        self.canvas_sim.create_rectangle(540, self.grua_y, 580, self.grua_y+10, fill="orange")
        
        if self.caixa_na_grua:
            self.canvas_sim.create_rectangle(545, self.grua_y+10, 575, self.grua_y+35, fill="#8B4513")
        elif self.caixa_no_carro:
            self.canvas_sim.create_rectangle(self.carro_x+25, 195, self.carro_x+55, 220, fill="#8B4513")

        # Atualizar Grafcet (Cores)
        for i, r in self.ui_etapas.items():
            self.canvas_graf.itemconfig(r, fill="#00ff00" if self.etapa == i else "#1a1a1a")

        conds = [self.inputs["M"] and self.inputs["a"], self.inputs["b"], self.grua_y <= 30 and self.etapa==2, self.inputs["a"]]
        for i, t in self.ui_trans.items():
            self.canvas_graf.itemconfig(t, fill="#00ff00" if conds[i] else "yellow")

        # Atualizar Monitor de I/O
        io_text = f" INPUTS (%I):\n"
        io_text += f" %I0.0 (M):   {self.inputs['M']}\n"
        io_text += f" %I0.1 (S_a): {self.inputs['a']}\n"
        io_text += f" %I0.2 (S_b): {self.inputs['b']}\n\n"
        io_text += f" OUTPUTS (%Q):\n"
        io_text += f" %Q0.0 (M1):  {1 if self.etapa==1 else 0}\n"
        io_text += f" %Q0.1 (M2):  {1 if self.etapa==3 else 0}\n"
        io_text += f" %Q0.2 (Grua):{1 if self.etapa==2 else 0}"
        self.lbl_io.config(text=io_text)

    def clique_start(self):
        if self.etapa == 0 and self.inputs["a"]:
            self.inputs["M"] = 1
            self.etapa = 1
            self.em_execucao = True

if __name__ == "__main__":
    root = tk.Tk()
    app = GrafcetGruaNormativo(root)
    root.mainloop()