# src/hook-main_pipeline.py
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('main_pipeline')
