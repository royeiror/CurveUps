# hook-curveup.py - PyInstaller hook file
from PyInstaller.utils.hooks import collect_all

# Force include all curveup modules
datas, binaries, hiddenimports = collect_all('curveup')
