from storyrealms.storyrealm_bridge import enter_storyrealm, step_realm, get_current_realm
import time

def main():
    print("Initializing AI World Building Engine...")
    result = enter_storyrealm("Genesis")
    print(f"Entered Realm: {result['realm']}")
    print("World Summary:", result['world_summary'])
    
    print("\n--- Simulation Start ---")
    for i in range(3):
        print(f"\nTick {i+1}:")
        step_result = step_realm()
        for log in step_result['logs']:
            print(f" - {log}")
        time.sleep(1)

    print("\n--- Simulation End ---")
    final_state = get_current_realm()
    print("Final State Summary:", final_state['summary'])

if __name__ == "__main__":
    main()
