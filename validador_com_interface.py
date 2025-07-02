import os
import time
import threading
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageSequence
from regra_validacao_produtos import validar_linha_produto, REGRAS_PRODUTO
from utils import limpar_para_contagem

cancelado = False

class ValidadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Validador de Planilhas de Produtos")
        self.root.configure(bg="#212121")
        self.root.geometry("800x400")
        self.root.resizable(False, False)
        self.entrada_path = tk.StringVar()
        self._center_window(800, 400)
        self._setup_style()
        self._build_widgets()
        self._load_gif_logo()
        self._start_time = None

    def _center_window(self, width, height):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TLabel", background="#212121", foreground="white", font=("Helvetica", 9))
        style.configure("TEntry", fieldbackground="#2b2b2b", foreground="white", borderwidth=0, relief="flat", font=("Helvetica", 9))
        style.configure("TProgressbar", troughcolor="#2b2b2b", background="#00ff88", borderwidth=0)

    def _build_widgets(self):
        main = tk.Frame(self.root, bg="#212121")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Top: Logo and Title
        top = tk.Frame(main, bg="#212121")
        top.pack(fill="x", pady=(0,5))
        
        # Logo
        self.logo_label = tk.Label(top, bg="#212121")
        self.logo_label.pack(side="left", anchor="nw")
        
        # Title Frame (centered)
        title_frame = tk.Frame(top, bg="#212121")
        title_frame.pack(side="left", padx=(150,0))
        tk.Label(title_frame, text="Validador de Planilhas de Produtos", 
                 bg="#212121", fg="white", font=("Helvetica",12,"bold")).pack(anchor="w")

        # Center: File selection
        center = tk.Frame(main, bg="#212121")
        center.pack(expand=True, fill="both", pady=10)
        cont = tk.Frame(center, bg="#212121")
        cont.place(relx=0.5, rely=0.5, anchor="center")
        
        # File selection components
        ttk.Label(cont, text="Arquivo Excel/CSV:", background="#212121", 
                  foreground="white").grid(row=0, column=0, sticky="e", padx=(0,5), pady=5)
        ttk.Entry(cont, textvariable=self.entrada_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        # Button container
        btnframe = tk.Frame(cont, bg="#212121")
        btnframe.grid(row=0, column=2, padx=(10,0))
        
        # Buttons
        tk.Button(btnframe, text="Procurar", command=self._selecionar_arquivo, 
                  bg="#444", fg="white", relief="flat", font=("Helvetica",9), 
                  padx=8, pady=4).pack(side="left", padx=5)
        
        self.btn_validar = tk.Button(btnframe, text="Executar Validação", 
                                     command=self._start_validation, bg="#333333", 
                                     fg="white", relief="flat", font=("Helvetica",9,"bold"), 
                                     padx=10, pady=5)
        self.btn_validar.pack(side="left", padx=5)
        
        self.btn_cancelar = tk.Button(btnframe, text="Parar", command=self._cancelar, 
                                      bg="#333333", fg="white", state="disabled", 
                                      relief="flat", font=("Helvetica",9,"bold"), 
                                      padx=10, pady=5)
        self.btn_cancelar.pack(side="left", padx=5)

        # Bottom: Progress bar and status
        bottom = tk.Frame(self.root, bg="#212121")
        bottom.pack(side="bottom", fill="x", padx=20, pady=(0,15))
        
        self.progresso = ttk.Progressbar(bottom, orient="horizontal", 
                                         length=600, mode="determinate")
        self.progresso.pack(fill="x", pady=(0,5))
        
        self.prog_label = tk.Label(bottom, text="", bg="#212121", 
                                   fg="#aaaaaa", font=("Helvetica",9))
        self.prog_label.pack()

        # Footer
        footer = tk.Frame(self.root, bg="#212121")
        footer.pack(side="bottom", fill="x", pady=(0,5))
        tk.Label(footer, text="© 2025 Sankhya BP ABC Paulistas. Direitos reservados.", 
                 bg="#212121", fg="#888888", font=("Helvetica",7)).pack(anchor="center")

        # Button hover effects
        for btn, color in [(self.btn_validar, "#00cc66"), (self.btn_cancelar, "#cc0000")]:
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#333333"))

    def _load_gif_logo(self):
        try:
            gif = Image.open("futuro_animado.gif")
            self.frames_logo = [ImageTk.PhotoImage(f.copy().resize((100,100), Image.Resampling.LANCZOS)) 
                               for f in ImageSequence.Iterator(gif)]
            self._animate_logo(0)
        except Exception:
            # Fallback if logo not found
            pass

    def _animate_logo(self, idx):
        frame = self.frames_logo[idx]
        self.logo_label.config(image=frame)
        self.logo_label.image = frame
        self.root.after(80, self._animate_logo, (idx+1) % len(self.frames_logo))

    def _selecionar_arquivo(self):
        path = filedialog.askopenfilename(filetypes=[("Excel/CSV", "*.xlsx;*.xls;*.csv")])
        if path:
            self.entrada_path.set(path)

    def _cancelar(self):
        global cancelado
        cancelado = True

    def _start_validation(self):
        global cancelado
        cancelado = False
        self._start_time = time.time()
        self.progresso.config(mode="indeterminate")
        self.progresso.start(10)
        self.btn_validar.config(state="disabled")
        self.btn_cancelar.config(state="normal")
        threading.Thread(target=self._run_validation, daemon=True).start()

    def _run_validation(self):
        global cancelado
        try:
            arquivo = self.entrada_path.get()
            if not os.path.exists(arquivo):
                raise FileNotFoundError("Arquivo não encontrado.")
            
            ext = os.path.splitext(arquivo)[1].lower()
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(arquivo, dtype=str)
            elif ext == '.csv':
                df = pd.read_csv(arquivo, dtype=str)
            else:
                raise RuntimeError("Formato não suportado")

            # Padronizar nomes de colunas
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Preencher colunas faltantes
            for col in REGRAS_PRODUTO.keys():
                if col not in df.columns:
                    df[col] = None

            if 'USO_PROD' in df.columns:
                df['USO_PROD'] = 'R'
            else:
                df['USO_PROD'] = 'R'

            total = len(df)
            self.progresso.config(mode="determinate", maximum=total, value=0)
            validos, invalidos = [], []

            for i, row in enumerate(df.itertuples(index=False), start=1):
                if cancelado:
                    raise Exception("Processo cancelado pelo usuário.")
                
                serie = pd.Series(row, index=df.columns)
                
                # Limpeza geral dos valores
                for col in serie.index:
                    if isinstance(serie[col], str):
                        serie[col] = limpar_para_contagem(serie[col])
                    elif pd.isna(serie[col]):
                        serie[col] = None
                
                # Validação específica para produtos
                ok, erros = validar_linha_produto(serie)
                
                if ok:
                    validos.append(serie)
                else:
                    serie['OBS_Validação'] = '; '.join(erros)
                    invalidos.append(serie)
                
                # Atualizar interface
                self.progresso['value'] = i
                self.prog_label.config(text=f"{i}/{total} | Inválidos: {len(invalidos)}")
                self.root.update_idletasks()

            # Salvar resultados
            os.makedirs('saida', exist_ok=True)
            if validos:
                pd.DataFrame(validos).to_excel('saida/produtos_validos.xlsx', index=False)
            if invalidos:
                pd.DataFrame(invalidos).to_excel('saida/produtos_invalidos.xlsx', index=False)
            
            messagebox.showinfo("Validação Concluída",
                               f"Produtos válidos: {len(validos)}\n" +
                               f"Produtos inválidos: {len(invalidos)}\n" +
                               f"Total processado: {total}")
        except Exception as e:
            messagebox.showwarning("Erro na Validação", str(e))
        finally:
            cancelado = False
            self.progresso.stop()
            self.btn_validar.config(state="normal")
            self.btn_cancelar.config(state="disabled")
            self.prog_label.config(text="Processo finalizado.")

if __name__ == '__main__':
    root = tk.Tk()
    ValidadorApp(root)
    root.mainloop()