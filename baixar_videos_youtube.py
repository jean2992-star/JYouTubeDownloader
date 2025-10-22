#!/usr/bin/env python3
"""
YouTube Downloader (yt-dlp + FFmpeg AutoFix)
---------------------------------------------
Ferramenta profissional para download de vídeos e áudios do YouTube.

📦 Recursos:
- Baixar vídeo (melhor qualidade)
- Baixar áudio em MP3
- Escolher pasta de saída personalizada
- Detecção automática do FFmpeg
- Atualização automática do yt-dlp
- Correção automática de containers com FFmpeg
- Tratamento de erros e mensagens coloridas

Autor: Jean Ivelsonne Dorvilma
GitHub: https://github.com/<seu-usuario>
Licença: MIT
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from yt_dlp import YoutubeDL

# ------------------------------------------------------------
# Configurações iniciais
# ------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
VIDEO_DIR = DOWNLOAD_DIR / "video"
AUDIO_DIR = DOWNLOAD_DIR / "audio"
for folder in [VIDEO_DIR, AUDIO_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# Funções utilitárias
# ------------------------------------------------------------
def print_header():
    """Exibe o cabeçalho principal do programa."""
    print("=" * 65)
    print("🎬  YouTube Downloader  (yt-dlp + FFmpeg AutoFix)")
    print("=" * 65)


def limpar_url(url: str) -> str:
    """Remove espaços ou barras inválidas no início da URL."""
    return url.strip().lstrip("/")


def verificar_ffmpeg() -> bool:
    """Verifica se o FFmpeg está instalado e acessível no PATH."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"✅ FFmpeg detectado: {ffmpeg_path}")
        return True
    else:
        print("⚠️ FFmpeg não encontrado. O programa ainda funciona, "
              "mas pode gerar erros de reprodução ou falhar na conversão para MP3.")
        print("➡️ Instale com:  choco install ffmpeg-full -y  (no Windows)")
        return False


def atualizar_yt_dlp():
    """Atualiza automaticamente o yt-dlp para a versão mais recente."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("🔄 yt-dlp atualizado com sucesso.")
    except Exception:
        print("⚠️ Falha ao atualizar yt-dlp (sem conexão ou permissão).")


def corrigir_video(caminho_arquivo: Path):
    """Corrige o container do vídeo usando FFmpeg (sem recodificar)."""
    if not verificar_ffmpeg():
        return
    try:
        novo_nome = caminho_arquivo.with_name(caminho_arquivo.stem + "_corrigido.mp4")
        print(f"🔧 Corrigindo vídeo com FFmpeg...")
        subprocess.run(
            ["ffmpeg", "-i", str(caminho_arquivo), "-c", "copy", str(novo_nome), "-y"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"✅ Vídeo corrigido salvo em: {novo_nome.name}")
    except Exception as e:
        print(f"⚠️ Erro ao corrigir vídeo: {e}")


# ------------------------------------------------------------
# Download de vídeo e áudio
# ------------------------------------------------------------
def progress_hook(d):
    """Monitora o progresso do download."""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()
        print(f"\r📥 Baixando: {percent} | {speed} | ETA: {eta}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\n✅ Download concluído!")


def baixar_video(url: str, pasta_saida: Path):
    """Baixa vídeo completo (melhor qualidade)."""
    ydl_opts = {
        'format': 'best',
        'outtmpl': str(pasta_saida / '%(title)s - %(id)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4'
    }
    try:
        print(f"\n🎥 Iniciando download do vídeo: {url}")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            caminho = Path(ydl.prepare_filename(info))
            corrigir_video(caminho)
    except Exception as e:
        print(f"\n❌ Erro ao baixar vídeo: {e}")


def baixar_audio(url: str, pasta_saida: Path):
    """Baixa apenas o áudio e converte para MP3."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(pasta_saida / '%(title)s - %(id)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'progress_hooks': [progress_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        print(f"\n🎧 Iniciando download do áudio (MP3): {url}")
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"\n❌ Erro ao baixar áudio: {e}")


# ------------------------------------------------------------
# Interface de menu
# ------------------------------------------------------------
def main():
    print_header()
    atualizar_yt_dlp()
    verificar_ffmpeg()

    print("1️⃣  Baixar vídeo completo (melhor qualidade)")
    print("2️⃣  Baixar apenas o áudio (MP3)")
    print("3️⃣  Escolher pasta de saída personalizada")
    print("=" * 65)

    opcao = input("Escolha uma opção (1/2/3): ").strip()
    url = limpar_url(input("\nCole o link do vídeo do YouTube: ").strip())

    if not url.startswith("http"):
        print("❌ URL inválida! Certifique-se de colar o link completo do YouTube.")
        return

    pasta_saida = VIDEO_DIR if opcao == "1" else AUDIO_DIR
    if opcao == "3":
        caminho = input("Digite o caminho da pasta de saída (ex: ./meus_videos): ").strip()
        pasta_saida = Path(caminho) if caminho else DOWNLOAD_DIR
        pasta_saida.mkdir(parents=True, exist_ok=True)
        tipo = input("Deseja baixar vídeo ou áudio? (v/a): ").lower()
        if tipo == "v":
            baixar_video(url, pasta_saida)
        else:
            baixar_audio(url, pasta_saida)
    elif opcao == "1":
        baixar_video(url, pasta_saida)
    elif opcao == "2":
        baixar_audio(url, pasta_saida)
    else:
        print("❌ Opção inválida!")


if __name__ == "__main__":
    main()
