from pathlib import Path

emoji_dir = Path(__file__).resolve().parent.parent / "img" / "emoji"

direction_cards = [
    {
        "title": "赚钱",
        "status": "not_configured",
        "icon_path": emoji_dir / "dollar.png",
        "created_phase": "onboarding"
    },
    {
        "title": "美白",
        "status": "pending_activation",
        "icon_path": emoji_dir / "makeup (1).png",
        "created_phase": "onboarding"
    },
    {
        "title": "爱好",
        "status": "not_configured",
        "icon_path": emoji_dir / "hobby.png",
        "created_phase": "onboarding"
    },
    {
        "title": "健身",
        "status": "pending_activation",
        "icon_path": emoji_dir / "fitness.png",
        "created_phase": "onboarding"
    }
]