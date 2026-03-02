#!/usr/bin/env python3
"""Render the email newsletter template with data from a YAML file.

Usage:
    python render.py              # render once
    python render.py --watch      # render and re-render on changes
    python render.py data.yaml    # render with alternate data file
"""

import sys
import time
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
WATCH_FILES = {"template.html.j2", "data.yaml"}


def render(data_file: Path) -> None:
    with open(data_file) as f:
        data = yaml.safe_load(f)

    env = Environment(
        loader=FileSystemLoader(BASE_DIR),
        keep_trailing_newline=True,
    )
    template = env.get_template("template.html.j2")
    output = template.render(**data)

    output_path = BASE_DIR / "email.html"
    output_path.write_text(output)
    print(f"[{time.strftime('%H:%M:%S')}] Rendered → email.html")


def watch(data_file: Path) -> None:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if Path(event.src_path).name in WATCH_FILES:
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
