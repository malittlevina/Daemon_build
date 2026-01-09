# scrolls/trigger_manager.py

from memory_tree.memory_logger import log_memory

def trigger_scroll(scroll_name, reason="user_request"):
    print(f"[TriggerManager] Scroll '{scroll_name}' invoked due to: {reason}")
    log_memory(f"Triggered scroll: {scroll_name}", context={"reason": reason})

def check_scroll_triggers(scrolls):
    print("[TriggerManager] Checking scroll triggers...")
    for scroll in scrolls:
        if 'trigger' in scroll and callable(scroll['trigger']):
            if scroll['trigger']():
                print(f"[TriggerManager] Trigger condition met for: {scroll['name']}")
                if 'action' in scroll and callable(scroll['action']):
                    scroll['action']()
