from pathlib import Path
from datetime import datetime
import json

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
wake_file = DATA_DIR / "wake_time.jsonl"


# as long as greeting part works, the data dir always exist
def create_data_dir():
    DATA_DIR.mkdir(exist_ok=True)

def append_wake_time_jsonl(record: dict) -> None:
    with open(wake_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def read_last_line_jsonl():
    with open(wake_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        return json.loads(lines[-1])

def decide_getup_time():
    create_data_dir()
    wake_file = DATA_DIR / "wake_time.jsonl"

    if wake_file.exists():
        last_line = read_last_line_jsonl()
        print(f"last_line['date']: {last_line['date']}")
        print(f"datetime.now().date().isoformat():{datetime.now().date().isoformat()}")

        if last_line["date"] != datetime.now().date().isoformat():
            wake_up_time = datetime.now().strftime("%H:%M")
            early = datetime.now().hour < 9

            if not early:
                streak = 0
            else:
                if last_line["early"]:
                    streak = last_line["streak"] + 1
                else:
                    streak = 1

            record = {
                "date": datetime.now().date().isoformat(),
                "wake_time": wake_up_time,
                "early": early,
                "streak": streak
            }
            append_wake_time_jsonl(record)
            return record

        else:
            return {
                "date": last_line["date"],
                "wake_time": last_line["wake_time"],
                "early": last_line["early"],
                "streak": last_line["streak"]
            }

    else:
        wake_up_time = datetime.now().strftime("%H:%M")
        early = datetime.now().hour < 9
        streak = 1 if early else 0

        record = {
            "date": datetime.now().date().isoformat(),
            "wake_time": wake_up_time,
            "early": early,
            "streak": streak
        }
        append_wake_time_jsonl(record)
        return record

def get_monthly_early_percentage():
    data = []

    if not wake_file.exists():
        return [0, 0]

    with open(wake_file, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    total_days = 0
    early_days = 0

    for record in data:
        date_obj = datetime.strptime(record["date"], "%Y-%m-%d")

        if date_obj.year == current_year and date_obj.month == current_month:
            total_days += 1
            if record["early"]:
                early_days += 1

    days_so_far = now.day

    conservative_progress_rate = round((early_days / days_so_far) * 100) if days_so_far else 0
    consistency_among_logged_days_rate = round((early_days / total_days) * 100) if total_days else 0

    return [conservative_progress_rate, consistency_among_logged_days_rate]