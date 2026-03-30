#!/usr/bin/env python3
"""Render email and landing page templates with shared data.

Reads events from gameplay.csv and static config from data.yaml.
Shows events from today onward (current month+future). If none exist,
falls back to the most recent month that has events.

Usage:
    python render.py              # render once
    python render.py --watch      # render and re-render on changes
"""

import csv
import io
import re
import sys
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent

TEMPLATES = [
    ("email.html.j2", "email.html"),
    ("index.html.j2", "index.html"),
]

WATCH_FILES = {"data.yaml", "email.html.j2", "index.html.j2"}

GAMEPLAY_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d"
    "/1omIVUX9-nvRWmMXTfH5N8gTG_qM6yYccwDCoHsMmYns"
    "/export?format=csv&gid=0"
)

EVENT_COLORS = ["#E8500A", "#3aad5e", "#c94040", "#4bbdad", "#e5a820"]


def parse_event_date(raw: str) -> tuple[datetime, str] | None:
    """Parse '3/1/25 at 10am' or '4/5/25 at 11am - 1pm' into (datetime, time_str)."""
    m = re.match(r"(\d+/\d+/\d+)\s+at\s+(.+)", raw.strip())
    if not m:
        return None
    date_part, time_part = m.group(1), m.group(2).strip()

    dt = datetime.strptime(date_part, "%m/%d/%y")

    time_str = re.sub(r"\s*-\s*", "–", time_part)

    return dt, time_str


def load_events(today: date | None = None) -> list[dict]:
    today = today or date.today()
    first_of_month = today.replace(day=1)

    with urllib.request.urlopen(GAMEPLAY_SHEET_URL) as resp:
        content = resp.read().decode("utf-8")

    all_events = []
    for row in csv.DictReader(io.StringIO(content)):
        parsed = parse_event_date(row["date"])
        if not parsed:
            continue
        dt, time_str = parsed
        hosts_raw = row.get("hosts", "").strip().strip('"')
        hosts = (
            " & ".join(h.strip() for h in hosts_raw.split(",")) if hosts_raw else ""
        )
        event_name = row.get("eventName", "").strip()

        all_events.append(
            {
                "dt": dt,
                "date_obj": dt.date(),
                "month": dt.strftime("%b"),
                "day": dt.day,
                "weekday": dt.strftime("%A"),
                "time": time_str,
                "hosts": hosts,
                "event_name": event_name,
            }
        )

    all_events.sort(key=lambda e: e["dt"])

    # Current month + future events
    upcoming = [e for e in all_events if e["date_obj"] >= first_of_month]

    if not upcoming:
        # Fall back to the last month that has events
        past = [e for e in all_events if e["date_obj"] < first_of_month]
        if past:
            last_month = past[-1]["date_obj"].replace(day=1)
            upcoming = [e for e in past if e["date_obj"] >= last_month]

    # Split into regular and special (have custom event name, no hosts) events
    regular = [e for e in upcoming if not (e["event_name"] and not e["hosts"])]
    special = [e for e in upcoming if e["event_name"] and not e["hosts"]]

    # Assign cycling colors and build final dicts
    def build_event_list(source):
        result = []
        for i, e in enumerate(source):
            label = e["event_name"] or e["hosts"] or "Open Play"
            result.append(
                {
                    "month": e["month"],
                    "day": e["day"],
                    "weekday": e["weekday"],
                    "time": e["time"],
                    "hosts": label,
                    "color": EVENT_COLORS[i % len(EVENT_COLORS)],
                }
            )
        return result

    return build_event_list(regular), build_event_list(special)


def render(data_file: Path) -> None:
    with open(data_file) as f:
        data = yaml.safe_load(f)

    data["events"], data["special_events"] = load_events()

    env = Environment(
        loader=FileSystemLoader(BASE_DIR),
        keep_trailing_newline=True,
    )

    for template_path, output_path in TEMPLATES:
        template = env.get_template(template_path)
        output = template.render(**data)
        (BASE_DIR / output_path).write_text(output)
        print(f"[{time.strftime('%H:%M:%S')}] Rendered → {output_path}")


def watch(data_file: Path) -> None:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            name = Path(event.src_path).name
            if name in WATCH_FILES:
                render(data_file)

    render(data_file)
    observer = Observer()
    observer.schedule(Handler(), str(BASE_DIR), recursive=False)
    observer.start()
    print("Watching for changes… (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    args = [a for a in sys.argv[1:] if a != "--watch"]
    data_file = Path(args[0]) if args else BASE_DIR / "data.yaml"

    if "--watch" in sys.argv:
        watch(data_file)
    else:
        render(data_file)


if __name__ == "__main__":
    main()
