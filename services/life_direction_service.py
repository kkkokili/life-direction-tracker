# ===== 功能：导入 AddDirectionDialog, ConfigDialog 弹窗类 =====
from dialogs.life_direction_add_direction_dialog import AddDirectionDialog
from dialogs.life_direction_configure_dialog import ConfigureDialog

from config.theme import (CARD_DEFAULT,CARD_PENDING_ACTIVATION,TAPE_ORANGE)

#draw_single_card里用到的方法,line 174
def handle_add_direction(page,event=None):
    dialog = AddDirectionDialog(page,on_save=lambda title, icon_path: save_new_direction(page, title, icon_path))
    dialog.update_idletasks()
    dialog.after(10, dialog.load_emojis)


# ===== 功能：接收弹窗保存回来的数据，并新增一张方向卡片 =====
def save_new_direction(page,title, icon_path):
    add_direction_card(
        page,
        title=title,
        status="not_configured",
        icon_path=icon_path,
        created_phase="onboarding"
    )

# ===== 功能：新增方向卡片，并支持保存 icon_path（png 图片路径） =====
def add_direction_card(
        page,
        title="新方向",
        status="not_configured",
        icon_path=None,
        created_phase="onboarding"
):
    page.direction_cards.append({

        "title": title,
        "status": status,
        "icon_path": icon_path,  # 新数据：png 图片路径
        "created_phase": created_phase
    })
    page.direction_cards.sort(
        key=lambda c: 0 if c["status"] == "not_configured" else 1
    )
    page.draw_ui()

#映射card样式
def get_card_ui(card):
    status = card["status"]

    match status:
        case "not_configured":
            return {
                "fill": CARD_DEFAULT,
                "status_text": "未配置",
                "status_color": "#9c7357",
                "tape": None
            }

        case "pending_activation":
            return {
                "fill": CARD_PENDING_ACTIVATION,
                "status_text": "",
                "status_color": "#9c7357",
                "tape": TAPE_ORANGE
            }

#点击每个direction card之后跳出来弹框编辑
def open_config_dialog(page, card):
    dialog = ConfigureDialog(
        page,
        direction_title=card["title"],
        on_save=save_direction_config
    )
    dialog.focus_force()

#这个还没写完
def save_direction_config(page, direction_title, config_data):
    for card in page.direction_cards:
        if card["title"] == direction_title:
            card["status"] = "pending_activation"
            card["config_data"] = config_data #这
            break

    page.direction_cards.sort(
        key=lambda c: 0 if c["status"] == "not_configured" else 1
    )
    page.draw_ui()