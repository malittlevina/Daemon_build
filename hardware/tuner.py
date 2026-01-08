from hardware.display import DisplayManager
from hardware.profiler import PerformanceProfiler

class DisplayAutoTuner:
    def __init__(self):
        self.display_mgr = DisplayManager()
        self.profiler = PerformanceProfiler()

    def optimize(self):
        """
        Analyzes hardware and adjusts display settings automatically.
        """
        # 1. Evaluate Hardware
        score = self.profiler.run_benchmark()
        
        # 2. Scan Displays
        displays = self.display_mgr.scan_displays()
        if not displays:
            return "No displays detected to optimize."
            
        target_display = displays[0] # Optimize primary
        name = target_display["name"]
        modes = target_display.get("modes", [])
        
        report = [f"Optimizing for {self.profiler.classification}..."]
        
        # 3. Apply Logic
        # Resolution Strategy
        target_res = None
        if score > 1500:
            # High End: Max Resolution
            report.append("High Performance detected: Preferring High Resolution/Refresh.")
            if modes: target_res = modes[0] # Assuming sorted by xrandr high->low
        elif score < 500:
            # Low End: Conservative Resolution
            report.append("Low Performance detected: Reducing Resolution for speed.")
            # Pick a middle mode if available
            if len(modes) > 2: target_res = modes[int(len(modes)/2)]
        
        # Apply Resolution
        if target_res:
             report.append(f"Setting resolution to {target_res}")
             # Parse width/height
             if "x" in target_res:
                 w, h = map(int, target_res.split("x"))
                 self.display_mgr.set_resolution(name, w, h)

        # Contrast/Gamma Strategy (Visual "Pop")
        # If machine is powerful, we might assume it's for media/gaming -> High Contrast
        if score > 1000:
             report.append("Enhancing contrast and saturation.")
             self.display_mgr.adjust_gamma_brightness(name, brightness=1.1, gamma="0.9:0.9:0.9")
        else:
             # Standard "Office" look
             self.display_mgr.adjust_gamma_brightness(name, brightness=1.0, gamma="1.0:1.0:1.0")

        return "\n".join(report)
