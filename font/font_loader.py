import os, sys
import ctypes

FR_PRIVATE = 0x10

def resource_path(rel_path: str) -> str:
    """兼容 PyInstaller: 开发环境/打包后 都能找到资源文件"""
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)

def load_private_font(ttf_rel_path: str) -> bool:
    """
    将字体临时加载到当前进程（不安装到系统）。
    成功后，你可以在 Tkinter 里用 font=("Inter", 20) 这样的 family 名称。
    """
    ttf_path = resource_path(ttf_rel_path)
    if not os.path.exists(ttf_path):
        raise FileNotFoundError(ttf_path)

    add_font = ctypes.windll.gdi32.AddFontResourceExW
    add_font.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
    added = add_font(ttf_path, FR_PRIVATE, None)
    return added > 0