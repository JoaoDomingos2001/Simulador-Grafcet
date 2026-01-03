import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

class LauncherIndustrial:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Automação Industrial")
        self.root.geometry("450x600") # Aumentei um pouco a altura para caber o novo botão
        self.root.configure(bg="#1e1e1e")

        # Título Estilizado
        tk.Label(root, text="SISTEMAS GRAFCET", bg="#1e1e1e", fg="#00ff00", 
                 font=("Courier", 18, "bold")).pack(pady=30)

        # Estilo dos Botões
        btn_config = {
            "font": ("Arial", 11, "bold"),
            "width": 30,
            "height": 2,
            "bd": 0,
            "cursor": "hand2",
            "activebackground": "#333",
            "activeforeground": "white"
        }

        # Botão para Exemplo 1: Grua
        tk.Button(root, text="📂 SIMULADOR GRUA & CARRINHO", bg="#2980b9", fg="white",
                  command=lambda: self.executar("exercicio_grua.py"), **btn_config).pack(pady=10)

        # Botão para Exemplo 2: Furadeira
        tk.Button(root, text="📂 SIMULADOR FURADEIRA", bg="#8e44ad", fg="white",
                  command=lambda: self.executar("exercicio_furadeira.py"), **btn_config).pack(pady=10)

        # --- NOVO BOTÃO: LÂMPADA ---
        tk.Button(root, text="💡 SIMULADOR LÂMPADA", bg="#f39c12", fg="white",
                  command=lambda: self.executar("exercicio_lampada.py"), **btn_config).pack(pady=10)

        tk.Button(root, text="⚙️ SIMULADOR MOTOR", bg="#32e622", fg="white",
          command=lambda: self.executar("exercicio_motor.py"), **btn_config).pack(pady=10)

        tk.Button(root, text="🔧 QUALIFICADORES", bg="#e622a5", fg="white",
          command=lambda: self.executar("exercicio_qualificadores.py"), **btn_config).pack(pady=10)
        
        tk.Button(root, text="♾️ ESTADOS ASSOCIADOS A ETAPAS ", bg="#d35400", fg="white",
          command=lambda: self.executar("exemplo_etapas.py"), **btn_config).pack(pady=10)

        # Espaçador
        tk.Frame(root, bg="#444", height=2).pack(fill="x", pady=20, padx=50)

        # Botão Sair
        tk.Button(root, text="❌ SAIR", bg="#c0392b", fg="white",
                  command=root.quit, **btn_config).pack(pady=10)

        self.lbl_status = tk.Label(root, text="Aguardando seleção...", bg="#1e1e1e", fg="gray")
        self.lbl_status.pack(side="bottom", pady=10)

    def executar(self, nome_ficheiro):
        # Deteta a pasta quer seja .py ou .exe
        caminho_atual = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        caminho_script = os.path.join(caminho_atual, nome_ficheiro)

        if os.path.exists(caminho_script):
            try:
                # Tenta executar usando o comando python do sistema
                subprocess.Popen(["python", caminho_script], shell=True)
                self.lbl_status.config(text=f"Lançado: {nome_ficheiro}", fg="#00ff00")
            except Exception as e:
                self.lbl_status.config(text="Erro ao lançar", fg="red")
                messagebox.showerror("Erro de Execução", f"Falha ao abrir o script:\n{e}")
        else:
            messagebox.showerror("Erro", f"Ficheiro não encontrado:\n{nome_ficheiro}\n\nLocal: {caminho_atual}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherIndustrial(root)
    root.mainloop()