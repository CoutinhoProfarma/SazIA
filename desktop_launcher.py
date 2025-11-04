# desktop_launcher.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
import subprocess
import sys
import os
import time
import signal

class SazonalLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Sazonal Analytics - Profarma")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Configurar estilo
        self.setup_styles()
        
        # Processo do servidor
        self.server_process = None
        
        # Criar interface
        self.create_widgets()
        
        # Fechar servidor ao fechar janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Configura estilos com cores da Profarma"""
        self.root.configure(bg='#14555a')
        
    def create_widgets(self):
        """Cria os widgets da interface"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#14555a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Logo/Título
        title_label = tk.Label(
            main_frame,
            text="PROFARMA\nSistema de Análise de Sazonalidade",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#14555a',
            pady=20
        )
        title_label.pack()
        
        # Frame de status
        status_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Label de status
        self.status_label = tk.Label(
            status_frame,
            text="Servidor: Parado",
            font=('Arial', 12),
            fg='#14555a',
            bg='white',
            pady=10
        )
        self.status_label.pack()
        
        # Área de log
        self.log_text = tk.Text(
            status_frame,
            height=8,
            width=50,
            font=('Consolas', 9),
            bg='#f0f0f0'
        )
        self.log_text.pack(padx=10, pady=10)
        
        # Frame de botões
        button_frame = tk.Frame(main_frame, bg='#14555a')
        button_frame.pack(fill=tk.X)
        
        # Botão Iniciar
        self.start_button = tk.Button(
            button_frame,
            text="Iniciar Sistema",
            command=self.start_server,
            bg='#00aeef',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Botão Abrir Navegador
        self.browser_button = tk.Button(
            button_frame,
            text="Abrir no Navegador",
            command=self.open_browser,
            bg='#f7941d',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor='hand2'
        )
        self.browser_button.pack(side=tk.LEFT, padx=5)
        
        # Botão Parar
        self.stop_button = tk.Button(
            button_frame,
            text="Parar Sistema",
            command=self.stop_server,
            bg='#b72026',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor='hand2'
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
    def log_message(self, message):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        
    def start_server(self):
        """Inicia o servidor Flask"""
        self.log_message("Iniciando servidor...")
        self.status_label.config(text="Servidor: Iniciando...", fg='orange')
        
        # Desabilitar botão iniciar, habilitar parar
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Iniciar servidor em thread separada
        thread = threading.Thread(target=self.run_server)
        thread.daemon = True
        thread.start()
        
        # Aguardar servidor iniciar e abrir navegador
        self.root.after(2000, self.server_started)
        
    def run_server(self):
        """Executa o servidor Flask"""
        try:
            # Usar subprocess para ter controle sobre o processo
            self.server_process = subprocess.Popen(
                [sys.executable, 'app_launcher.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except Exception as e:
            self.log_message(f"Erro ao iniciar servidor: {e}")
            self.status_label.config(text="Servidor: Erro", fg='red')
            
    def server_started(self):
        """Ações após servidor iniciar"""
        self.status_label.config(text="Servidor: Rodando", fg='green')
        self.browser_button.config(state=tk.NORMAL)
        self.log_message("Servidor iniciado com sucesso!")
        self.log_message("Abrindo navegador...")
        self.open_browser()
        
    def open_browser(self):
        """Abre o navegador"""
        webbrowser.open('http://127.0.0.1:5000/')
        self.log_message("Navegador aberto")
        
    def stop_server(self):
        """Para o servidor Flask"""
        self.log_message("Parando servidor...")
        
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            
        self.status_label.config(text="Servidor: Parado", fg='#14555a')
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.browser_button.config(state=tk.DISABLED)
        self.log_message("Servidor parado")
        
    def on_closing(self):
        """Ao fechar a janela"""
        if self.server_process:
            if messagebox.askokcancel("Sair", "Deseja parar o servidor e sair?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = SazonalLauncher(root)
    root.mainloop()
