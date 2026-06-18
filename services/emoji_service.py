from config.theme import (
    EMOJI_SIZE_2, TILE_SIZE_2, EMOJI_COLS_2,EMOJI_SIZE_1, TILE_SIZE_1, EMOJI_COLS_1, BG_MAIN
)
from PIL import Image, ImageTk, ImageOps
from pathlib import Path
import tkinter as tk

# ===== emoji分批加载控制 =====
batch_size = 8
# ===== 布局常量 =====
start_y = 8
gap_x = 18
gap_y = 10

# ===== emoji 数据与状态 =====
emoji_dir = Path(__file__).resolve().parent.parent / "img" / "emoji"

# =========================
# 4. emoji 选择区域
# =========================
def build_emoji_picker(page):
    outer = tk.Frame(page, bg="#f7f3ef")

    if page.emoji_preset == "large":
        outer.pack(fill="both", expand=True, padx=38, pady=(0, 16))
    else:
        outer.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    picker_box = tk.Frame(
        outer,
        bg="white",
        highlightthickness=1,
        highlightbackground="#e3d9d1"
    )
    picker_box.pack(fill="both", expand=True)

    # 1. 先创建 scrollbar，但先不要绑定 command
    page.scrollbar = tk.Scrollbar(
        picker_box,
        orient="vertical"
    )

    if page.emoji_preset == "large":
        page.scrollbar.pack(side="right", fill="y", padx=(0, 14), pady=16)
    else:
        page.scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 4),
            pady=8,
            ipadx=4
        )

    # 2. 再创建 canvas
    page.emoji_canvas = tk.Canvas(
        picker_box,
        bg="white",
        highlightthickness=0,
        bd=0
    )

    if page.emoji_preset == "large":
        page.emoji_canvas.pack(side="left", fill="both", expand=True, padx=(16, 6), pady=16)
    else:
        page.emoji_canvas.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)

    # 3. 最后双向绑定 scrollbar 和 canvas
    page.scrollbar.configure(command=page.emoji_canvas.yview)
    page.emoji_canvas.configure(yscrollcommand=page.scrollbar.set)

    page.emoji_canvas.bind("<Enter>", lambda event: bind_mousewheel(page, event))
    page.emoji_canvas.bind("<Leave>", lambda event: unbind_mousewheel(page, event))

    page.loading_id = page.emoji_canvas.create_text(
        20, 20,
        text="Loading emojis...",
        anchor="nw",
        font=("Microsoft YaHei UI", 14),
        fill="#8b7462"
    )


# =========================
# 5. 滚轮
# =========================
def bind_mousewheel(page, event=None):
    page.bind_all("<MouseWheel>", lambda event:on_mousewheel(page, event))


def unbind_mousewheel(page, event=None):
    page.unbind_all("<MouseWheel>")


def on_mousewheel(page, event):
    page.emoji_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# =========================
# 6. 裁透明边 + 缩放
# =========================
def prepare_emoji_image(emoji_size, img_path):
    pil_img = Image.open(img_path).convert("RGBA")

    alpha = pil_img.getchannel("A")
    bbox = alpha.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)

    pil_img = ImageOps.contain(pil_img, emoji_size, Image.LANCZOS)
    return pil_img


# =========================
# 7. 固定底板
# =========================
def make_emoji_tile(page,img_path):
    if page.emoji_preset == "large":
        tile_size = TILE_SIZE_1
        emoji_size=EMOJI_SIZE_1
    else:
        tile_size = TILE_SIZE_2
        emoji_size=EMOJI_SIZE_2

    pil_img = prepare_emoji_image(emoji_size, img_path)

    tile = Image.new("RGBA", tile_size, (255, 255, 255, 0))
    x = (tile_size[0] - pil_img.width) // 2
    y = (tile_size[1] - pil_img.height) // 2
    tile.paste(pil_img, (x, y), pil_img)
    return tile


# =========================
# 8. 开始加载 emoji
# =========================
def load_emojis(page):
    print("LOAD EMOJIS CALLED BY:", page)
    if not emoji_dir.exists():
        page.emoji_canvas.itemconfig(
            page.loading_id,
            text=f"没有找到目录：\n{emoji_dir}"
        )
        return

    page.emoji_files = sorted(emoji_dir.glob("*.png"))

    if not page.emoji_files:
        page.emoji_canvas.itemconfig(
            page.loading_id,
            text="img/emoji 文件夹里还没有 png 图片。"
        )
        return

    page.emoji_canvas.delete(page.loading_id)
    page.load_index = 0

    # 先让弹窗稳定显示，再开始第一批
    page.after(1, lambda:load_emoji_batch(page))


# =========================
# 9. 分批加载
# =========================
def load_emoji_batch(page):
    if page.emoji_preset == "large":
        emoji_size = EMOJI_SIZE_1
        tile_size = TILE_SIZE_1
        emoji_cols = EMOJI_COLS_1
    else:
        emoji_size = EMOJI_SIZE_2
        tile_size = TILE_SIZE_2
        emoji_cols = EMOJI_COLS_2

    end_index = min(page.load_index + batch_size, len(page.emoji_files))

    page.emoji_canvas.update_idletasks()
    canvas_w = page.emoji_canvas.winfo_width()

    grid_w = (
            emoji_cols * tile_size[0]
            + (emoji_cols - 1) * gap_x
    )

    start_x = max(8, (canvas_w - grid_w) // 2)

    for index in range(page.load_index, end_index):
        img_path = page.emoji_files[index]

        row = index // emoji_cols
        col = index % emoji_cols

        x1 = start_x + col * (tile_size[0] + gap_x)
        y1 = start_y + row * (tile_size[1] + gap_y)
        x2 = x1 + tile_size[0]
        y2 = y1 + tile_size[1]

        try:
            bg_id = page.emoji_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="white",
                outline="",
                width=0
            )

            pil_img = make_emoji_tile(page,
                img_path

            )
            photo = ImageTk.PhotoImage(pil_img)
            page.emoji_photos.append(photo)

            img_id = page.emoji_canvas.create_image(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                image=photo
            )

            icon_path = str(img_path)
            page.emoji_bg_map[icon_path] = bg_id
            page.emoji_img_map[icon_path] = img_id
            page.emoji_item_map[bg_id] = icon_path
            page.emoji_item_map[img_id] = icon_path

            page.emoji_canvas.tag_bind(bg_id, "<Button-1>", lambda event:handle_canvas_emoji_click(page,event))
            page.emoji_canvas.tag_bind(img_id, "<Button-1>", lambda event: handle_canvas_emoji_click(page, event))

        except Exception:
            pass


    page.load_index = end_index

    total_rows = (len(page.emoji_files) + emoji_cols - 1) // emoji_cols
    content_h = start_y + total_rows * tile_size[1] + max(0, total_rows - 1) * gap_y + 24


    page.emoji_canvas.configure(
        scrollregion=(0, 0, 640, content_h)
    )

    if page.load_index < len(page.emoji_files):
        page.after(1, lambda:load_emoji_batch(page))


# =========================
# 10. Canvas 点击 emoji
# =========================
def handle_canvas_emoji_click(page, event):
    current = page.emoji_canvas.find_withtag("current")
    if not current:
        return

    item_id = current[0]
    icon_path = page.emoji_item_map.get(item_id)
    if not icon_path:
        return

    select_emoji(page, icon_path)


# =========================
# 11. 选中效果
# =========================
def select_emoji(page, icon_path):
    for path, bg_id in page.emoji_bg_map.items():
        page.emoji_canvas.itemconfig(
            bg_id,
            fill="white",
            outline="",
            width=0
        )

    page.selected_icon_path = icon_path

    bg_id = page.emoji_bg_map[icon_path]
    page.emoji_canvas.itemconfig(
        bg_id,
        fill="#fff3e8",
        outline="#e79a61",
        width=2
    )