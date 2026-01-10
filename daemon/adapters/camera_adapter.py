from __future__ import annotations

import threading
import time

from daemon.event_bus import EventBus
from daemon.events import DaemonEvent


def start_camera_watcher(bus: EventBus, *, interval_s: float = 5.0) -> threading.Thread:
    """
    Camera adapter using `sensors.vision.VisionSensor` if available.
    Publishes `vision_label` events (scene classification).
    """

    def run() -> None:
        try:
            from sensors.vision import VisionSensor  # type: ignore
        except Exception as e:
            bus.publish(
                DaemonEvent(
                    type="system_event",
                    payload={"component": "camera", "error": f"VisionSensor unavailable: {e}"},
                    source="camera",
                )
            )
            return

        try:
            sensor = VisionSensor()
        except Exception as e:
            bus.publish(
                DaemonEvent(
                    type="system_event",
                    payload={"component": "camera", "error": f"Camera init failed: {e}"},
                    source="camera",
                )
            )
            return

        print("[Camera] Watching scene classification.")
        last = None
        while True:
            try:
                scene = sensor.classify_scene()
                if scene and scene != last:
                    last = scene
                    bus.publish(
                        DaemonEvent(
                            type="vision_label",
                            payload={"scene": scene},
                            source="camera",
                        )
                    )
            except Exception as e:
                bus.publish(
                    DaemonEvent(
                        type="system_event",
                        payload={"component": "camera", "error": str(e)},
                        source="camera",
                    )
                )
            time.sleep(interval_s)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t

