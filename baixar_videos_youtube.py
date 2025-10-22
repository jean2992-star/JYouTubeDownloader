#!/usr/bin/env python3
# =============================================================
#  JYouTubeDownloader v2.0
#  Desenvolvido por: Jean Ivelsonne Dorvilma
#  Universidade Federal da Fronteira Sul – UFFS
#  Tema: Escuro Neon (Tkinter + yt-dlp + FFmpeg)
# =============================================================

import os
import threading
import shutil
from datetime import datetime
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from yt_dlp import YoutubeDL
import webbrowser

# -------------------------------------------------------------
# CONFIGURAÇÕES INICIAIS
# -------------------------------------------------------------
APP_NAME = "JYouTubeDownloader"
COR_PRINCIPAL = "#00ff99"
COR_FUNDO = "#1e1e1e"
COR_TEXTO = "white"

# Caminhos padrão
PASTA_VIDEOS = Path.home() / "Videos" / APP_NAME / "video"
PASTA_AUDIOS = Path.home() / "Videos" / APP_NAME / "audio"
PASTA_LOGS = Path(__file__).parent / "logs"
PASTA_LOGS.mkdir(parents=True, exist_ok=True)

# Cria pastas se não existirem
for pasta in [PASTA_VIDEOS, PASTA_AUDIOS]:
    pasta.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------
# FUNÇÕES PRINCIPAIS
# -------------------------------------------------------------
def verificar_ffmpeg():
    """Verifica se o FFmpeg está instalado"""
    if shutil.which("ffmpeg"):
        return True
    messagebox.showwarning(
        "FFmpeg não encontrado",
        "⚠️ FFmpeg não está instalado.\n\nBaixe em: https://www.gyan.dev/ffmpeg/builds/"
    )
    return False


def salvar_historico(tipo, titulo, url):
    """Registra no arquivo de histórico"""
    historico = PASTA_LOGS / "historico.txt"
    with open(historico, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M}] {tipo} - \"{titulo}\" - {url}\n")


def progresso_hook(d):
    """Atualiza a barra de progresso"""
    if d["status"] == "downloading":
        porcentagem = d.get("_percent_str", "0%").replace("%", "")
        progress_bar["value"] = float(porcentagem)
        status_label.config(text=f"Baixando... {porcentagem}%")
        root.update_idletasks()
    elif d["status"] == "finished":
        status_label.config(text="Processando com FFmpeg...")


def iniciar_download():
    """Inicia o processo de download"""
    url = entry_url.get().strip()
    nome_personalizado = entry_nome.get().strip()
    tipo = tipo_var.get()

    if not url.startswith("http"):
        messagebox.showerror("Erro", "Insira um link válido do YouTube.")
        return

    pasta_saida = PASTA_VIDEOS if tipo == "video" else PASTA_AUDIOS

    threading.Thread(target=lambda: baixar(url, nome_personalizado, tipo, pasta_saida)).start()


def baixar(url, nome, tipo, pasta):
    """Executa o download"""
    try:
        status_label.config(text="Iniciando download...")
        progress_bar["value"] = 0

        nome_arquivo = nome if nome else "%(title)s - %(id)s"
        saida = os.path.join(pasta, f"{nome_arquivo}.%(ext)s")

        opcoes = {
            "outtmpl": saida,
            "progress_hooks": [progresso_hook],
            "quiet": True,
            "noplaylist": True
        }

        if tipo == "video":
            opcoes["format"] = "best"
            opcoes["merge_output_format"] = "mp4"
        else:
            opcoes["format"] = "bestaudio/best"
            opcoes["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]

        with YoutubeDL(opcoes) as ydl:
            info = ydl.extract_info(url, download=True)
            titulo = info.get("title", "Desconhecido")
            salvar_historico(tipo.capitalize(), titulo, url)

        messagebox.showinfo("Sucesso", "✅ Download concluído com sucesso!")
        status_label.config(text="✅ Download concluído!")

    except Exception as e:
        messagebox.showerror("Erro", f"❌ Erro ao baixar:\n{e}")
        status_label.config(text="Erro no download.")


def abrir_pasta():
    """Abre a pasta de downloads"""
    pasta = PASTA_VIDEOS if tipo_var.get() == "video" else PASTA_AUDIOS
    os.startfile(pasta)


def alternar_tema():
    """Alterna entre tema claro e escuro"""
    global modo_escuro
    modo_escuro = not modo_escuro

    if modo_escuro:
        root.configure(bg=COR_FUNDO)
        style.configure("TLabel", background=COR_FUNDO, foreground=COR_TEXTO)
        style.configure("TButton", background=COR_PRINCIPAL)
        tema_btn.config(text="🌞 Tema Claro")
    else:
        root.configure(bg="white")
        style.configure("TLabel", background="white", foreground="black")
        style.configure("TButton", background="#0078D7")
        tema_btn.config(text="🌙 Tema Escuro")


def abrir_github():
    """Abre o repositório do projeto"""
    webbrowser.open("https://github.com/Jean2992-star/JYouTubeDownloader")


# -------------------------------------------------------------
# INTERFACE GRÁFICA (TKINTER)
# -------------------------------------------------------------
root = Tk()
root.title(f"{APP_NAME} – Tema Escuro")
root.geometry("640x460")
root.configure(bg=COR_FUNDO)
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

# Cabeçalho
Label(root, text="🎬 JYouTubeDownloader", font=("Segoe UI", 18, "bold"),
      bg=COR_FUNDO, fg=COR_PRINCIPAL).pack(pady=10)

# Campo de URL
Label(root, text="Cole o link do vídeo:", bg=COR_FUNDO, fg=COR_TEXTO).pack(anchor="w", padx=30)
entry_url = ttk.Entry(root, width=70)
entry_url.pack(padx=30, pady=5)

# Campo de nome
Label(root, text="Nome do arquivo (opcional):", bg=COR_FUNDO, fg=COR_TEXTO).pack(anchor="w", padx=30)
entry_nome = ttk.Entry(root, width=70)
entry_nome.pack(padx=30, pady=5)

# Tipo de download
tipo_var = StringVar(value="video")
frame_tipo = Frame(root, bg=COR_FUNDO)
frame_tipo.pack(pady=5)
Radiobutton(frame_tipo, text="🎥 Vídeo (MP4)", variable=tipo_var, value="video",
            bg=COR_FUNDO, fg=COR_TEXTO, selectcolor="#333").grid(row=0, column=0, padx=10)
Radiobutton(frame_tipo, text="🎧 Áudio (MP3)", variable=tipo_var, value="audio",
            bg=COR_FUNDO, fg=COR_TEXTO, selectcolor="#333").grid(row=0, column=1, padx=10)

# Botões
frame_botoes = Frame(root, bg=COR_FUNDO)
frame_botoes.pack(pady=15)
ttk.Button(frame_botoes, text="⬇️ Baixar", command=iniciar_download).grid(row=0, column=0, padx=10)
ttk.Button(frame_botoes, text="📂 Abrir Pasta", command=abrir_pasta).grid(row=0, column=1, padx=10)
tema_btn = ttk.Button(frame_botoes, text="🌞 Tema Claro", command=alternar_tema)
tema_btn.grid(row=0, column=2, padx=10)

# Barra de progresso
progress_bar = ttk.Progressbar(root, length=520, mode="determinate")
progress_bar.pack(pady=10)

# Status
status_label = Label(root, text="Aguardando link...", bg=COR_FUNDO, fg=COR_TEXTO)
status_label.pack(pady=10)

# Rodapé
ttk.Button(root, text="🌐 GitHub", command=abrir_github).pack(pady=5)

# FFmpeg
verificar_ffmpeg()

modo_escuro = True
root.mainloop()
