"""
Run this script while the AMS360 Renew window is open on screen.

Modes:
  python tools/inspect_renew_window.py              → full dump to logs/renew_window_controls.txt
  python tools/inspect_renew_window.py combo        → list all ComboBox values in the window
  python tools/inspect_renew_window.py search <kw>  → search all controls whose title/auto_id contains keyword
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pywinauto import Desktop

OUTPUT_FILE     = "logs/renew_window_controls.txt"
WINDOW_TITLE_RE = "Create Renewal/Rewrite Policy"


def get_window():
    print(f"Looking for window matching: '{WINDOW_TITLE_RE}'")
    win = Desktop(backend="uia").window(title_re=WINDOW_TITLE_RE)
    win.set_focus()
    print(f"Found: {win.window_text()}\n")
    return win


def dump_all(win):
    Path("logs").mkdir(exist_ok=True)
    print(f"Dumping all controls to {OUTPUT_FILE} ...")
    original_stdout = sys.stdout
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        sys.stdout = f
        win.print_control_identifiers(depth=None)
    sys.stdout = original_stdout
    print(f"Done. Open '{OUTPUT_FILE}' and search for what you need.")


def print_control_info(ctrl, indent=0):
    try:
        title   = ctrl.window_text() or "(no title)"
        auto_id = ctrl.element_info.automation_id or "(no auto_id)"
        ctype   = ctrl.element_info.control_type or "?"
        print(f"{'  ' * indent}{ctype} | title='{title}' | auto_id='{auto_id}'")
    except Exception:
        pass


def list_combo_values(win):
    """List all ComboBox controls and their items found anywhere in the Renew window."""
    print("=== All ComboBoxes in Renew window ===\n")
    combos = win.descendants(control_type="ComboBox")
    if not combos:
        print("No ComboBox found in the Renew window.")
        return
    for combo in combos:
        try:
            name    = combo.window_text() or "(no title)"
            auto_id = combo.element_info.automation_id or "(no auto_id)"
            print(f"ComboBox: '{name}'  auto_id='{auto_id}'")
            items = combo.item_texts()
            if items:
                for i, item in enumerate(items):
                    print(f"  [{i}] {item}")
            else:
                print("  (no items — open the dropdown first)")
            print()
        except Exception as e:
            print(f"  Error reading combo: {e}\n")


def search_all_controls(win, keyword: str):
    """Search every control in the window for a keyword in title or auto_id."""
    print(f"=== Searching all controls for: '{keyword}' ===\n")
    keyword_lower = keyword.lower()
    found = 0
    for ctrl in win.descendants():
        try:
            title   = ctrl.window_text() or ""
            auto_id = ctrl.element_info.automation_id or ""
            if keyword_lower in title.lower() or keyword_lower in auto_id.lower():
                print_control_info(ctrl)
                found += 1
        except Exception:
            pass
    print(f"\nFound {found} match(es) for '{keyword}'.")


def main():
    win  = get_window()
    mode = sys.argv[1] if len(sys.argv) > 1 else "dump"

    if mode == "combo":
        list_combo_values(win)

    elif mode == "search":
        if len(sys.argv) < 3:
            print("Usage: python tools/inspect_renew_window.py search <keyword>")
            print("Example: python tools/inspect_renew_window.py search EffectiveDate")
        else:
            search_all_controls(win, sys.argv[2])

    else:
        dump_all(win)


if __name__ == "__main__":
    main()
