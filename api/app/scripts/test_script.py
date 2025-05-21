import time

def run_script(emit_fn=print):
    for i in range(10):
        emit_fn(f"Ligne {i}")
        time.sleep(1)

if __name__ == "__main__":
    run_script()