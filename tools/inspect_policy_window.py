"""
Run this script while the AMS360 policy window is open on screen.

Modes:
  python tools/inspect_window.py              → full dump to logs/window_controls.txt
  python tools/inspect_window.py combo        → list ComboBox values in Transaction Fees section
  python tools/inspect_window.py basic        → list all controls in Basic Policy Info section
  python tools/inspect_window.py status       → find Status field auto_id in Basic Policy Info
  python tools/inspect_window.py search <kw>  → search all controls whose title/auto_id contains keyword
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pywinauto import Desktop

OUTPUT_FILE           = "logs/window_controls.txt"
WINDOW_TITLE_RE       = "Policy.*Policy Information"
FEES_PANE_AUTO_ID     = "sctPolicy_PolPremNonPrem_PolFeesTax"
BASIC_INFO_AUTO_ID    = "sctPolicy_PolBPolInfo"


def get_window():
    print(f"Looking for window: '{WINDOW_TITLE_RE}'")
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
    """List all ComboBox values inside the Transaction Fees section (after clicking New)."""
    print("=== ComboBoxes in Transaction Fees section ===")
    print("(Click 'New' in the fees section first)\n")
    try:
        fees_pane = win.child_window(auto_id=FEES_PANE_AUTO_ID, control_type="Pane")
        combos = fees_pane.descendants(control_type="ComboBox")
        if not combos:
            print("No ComboBox found. Make sure 'New' was clicked first.")
            return
        for combo in combos:
            try:
                name    = combo.window_text() or "(no title)"
                auto_id = combo.element_info.automation_id or "(no auto_id)"
                print(f"\nComboBox: '{name}'  auto_id='{auto_id}'")
                items = combo.item_texts()
                if items:
                    for i, item in enumerate(items):
                        print(f"  [{i}] {item}")
                else:
                    print("  (no items — open the dropdown first)")
            except Exception as e:
                print(f"  Error: {e}")
    except Exception as e:
        print(f"Could not reach fees pane: {e}")


def list_basic_info_controls(win):
    """List all controls inside the Basic Policy Information section."""
    print("=== All controls in Basic Policy Information section ===")
    print(f"(pane auto_id: '{BASIC_INFO_AUTO_ID}')\n")
    try:
        pane = win.child_window(auto_id=BASIC_INFO_AUTO_ID, control_type="Pane")
        for ctrl in pane.descendants():
            print_control_info(ctrl)
    except Exception as e:
        print(f"Could not reach Basic Policy Info pane: {e}")
        print("Make sure the section is expanded (click the section header first).")


def find_status_field(win):
    """Search for the Status field in the Basic Policy Information section."""
    print("=== Searching for Status field in Basic Policy Info ===\n")
    keywords = ["status", "polstatus", "Status"]
    found = []
    try:
        pane = win.child_window(auto_id=BASIC_INFO_AUTO_ID, control_type="Pane")
        for ctrl in pane.descendants():
            try:
                title   = (ctrl.window_text() or "").lower()
                auto_id = (ctrl.element_info.automation_id or "").lower()
                ctype   = ctrl.element_info.control_type or ""
                if any(k.lower() in title or k.lower() in auto_id for k in keywords):
                    found.append(ctrl)
                    print_control_info(ctrl)
            except Exception:
                pass
    except Exception as e:
        print(f"Could not reach Basic Policy Info pane: {e}")

    if not found:
        print("No Status field found in Basic Policy Info section.")
        print("Tips:")
        print("  1. Expand the Basic Policy Information section first")
        print("  2. Run:  python tools/inspect_window.py basic")
        print("     then search the output for 'status' manually")


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

    elif mode == "basic":
        list_basic_info_controls(win)

    elif mode == "status":
        find_status_field(win)

    elif mode == "search":
        if len(sys.argv) < 3:
            print("Usage: python tools/inspect_window.py search <keyword>")
            print("Example: python tools/inspect_window.py search Status")
        else:
            search_all_controls(win, sys.argv[2])

    else:
        dump_all(win)


if __name__ == "__main__":
    main()
