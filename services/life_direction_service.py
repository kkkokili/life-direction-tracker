from pathlib import Path
from pprint import pformat

from dialogs.life_direction_add_direction_dialog import AddDirectionDialog
from dialogs.life_direction_configure_dialog import ConfigureDialog

from config.theme import CARD_DEFAULT, CARD_PENDING_ACTIVATION, TAPE_ORANGE


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIFE_DIRECTION_REPO_PATH = PROJECT_ROOT / "data" / "life_direction_repo.py"


def get_status_rank(status):
    ranks = {
        "not_configured": 0,
        "incomplete": 1,
        "pending_activation": 1,
    }
    return ranks.get(status, 0)


def sort_direction_cards(page):
    page.direction_cards.sort(
        key=lambda card: get_status_rank(card.get("status"))
    )


def serialize_value(value):
    if isinstance(value, Path):
        try:
            return value.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            return str(value)

    if isinstance(value, str):
        path_value = Path(value)
        if path_value.is_absolute():
            try:
                return path_value.relative_to(PROJECT_ROOT).as_posix()
            except ValueError:
                return value
        return value

    if isinstance(value, dict):
        return {
            key: serialize_value(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [serialize_value(item) for item in value]

    if isinstance(value, tuple):
        return tuple(serialize_value(item) for item in value)

    return value


def save_direction_cards_to_repo(page):
    serialized_cards = serialize_value(page.direction_cards)
    content = (
        "from pathlib import Path\n\n"
        "# This file is updated by the app when life directions are saved.\n\n"
        f"direction_cards = {pformat(serialized_cards, width=100, sort_dicts=False)}\n"
    )
    LIFE_DIRECTION_REPO_PATH.write_text(content, encoding="utf-8")


def handle_add_direction(page, event=None):
    dialog = AddDirectionDialog(
        page,
        on_save=lambda title, icon_path: save_new_direction(page, title, icon_path)
    )
    dialog.update_idletasks()
    dialog.after(10, dialog.load_emojis)


def save_new_direction(page, title, icon_path):
    add_direction_card(
        page,
        title=title,
        status="not_configured",
        icon_path=icon_path,
        created_phase="onboarding"
    )


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
        "icon_path": icon_path,
        "created_phase": created_phase
    })
    sort_direction_cards(page)
    save_direction_cards_to_repo(page)
    page.draw_ui()


def get_card_ui(card):
    status = card.get("status", "not_configured")

    match status:
        case "not_configured":
            return {
                "fill": CARD_DEFAULT,
                "status_text": "未配置",
                "status_color": "#9c7357",
                "tape": None
            }
        case "incomplete":
            return {
                "fill": CARD_DEFAULT,
                "status_text": "未配置完",
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
        case _:
            return {
                "fill": CARD_DEFAULT,
                "status_text": "未配置",
                "status_color": "#9c7357",
                "tape": None
            }


def open_config_dialog(page, card):
    dialog = ConfigureDialog(
        page,
        direction_title=card["title"],
        on_save=save_direction_config,
        initial_data=card.get("config_data")
    )
    dialog.focus_force()


def is_section_configured(section):
    if not section.get("is_configured", False):
        return False

    child_sections = section.get("sections", [])
    if child_sections:
        return all(is_section_configured(child) for child in child_sections)

    return bool(section.get("seeds", []))


def get_config_data_status(config_data):
    sections = config_data.get("sections", [])
    seeds = config_data.get("seeds", [])

    if not sections and not seeds:
        return "not_configured"

    if not sections and seeds:
        return "pending_activation"

    if all(is_section_configured(section) for section in sections):
        return "pending_activation"

    return "incomplete"


def save_direction_config(page, direction_title, config_data):
    for card in page.direction_cards:
        if card["title"] == direction_title:
            card["status"] = get_config_data_status(config_data)
            card["config_data"] = config_data
            if card["status"] == "pending_activation":
                page.direction_cards.remove(card)
                page.direction_cards.append(card)
            break

    save_direction_cards_to_repo(page)
    page.draw_ui()
