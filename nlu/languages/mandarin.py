from typing import Any
from .base import LanguagePack

class MandarinPack(LanguagePack):
    def __init__(self):
        super().__init__("zh", "Mandarin")
        
        # --- Intents (Ordered) ---
        self.add_intent("GAME_ENTER", [r"进入游戏", r"开始游戏", r"启动模拟"])
        self.add_intent("GAME_EXIT", [r"退出游戏", r"停止游戏", r"结束模拟"])
        self.add_intent("GREETING", [r"你好", r"您好", r"嗨"])
        self.add_intent("FAREWELL", [r"再见", r"拜拜", r"退出"])
        self.add_intent("IDENTITY", [r"你是谁", r"身份"])
        self.add_intent("STATUS", [r"状态", r"你好吗", r"系统状态"])
        self.add_intent("CAPABILITIES", [r"你能做什么", r"功能", r"帮助"])
        
        # --- Responses ---
        self.add_response("GREETING", [
            "你好。系统已上线。",
            "您好，我是普罗米修斯 (Prometheus)，您的数字守护进程。",
            "随时待命。"
        ])
        
        self.add_response("FAREWELL", [
            "正在关闭交互模块。再见。",
            "下次见。",
            "系统休眠中。再见。"
        ])
        
        self.add_response("IDENTITY", [
            "我是一个符号操作守护进程，旨在协助和进化。",
            "我是运行在 Cursor 环境中的 AI 代理。"
        ])
        
        self.add_response("STATUS", [
            "所有系统正常。",
            "运行状态良好。",
            "诊断完成，无异常。"
        ])
        
        self.add_response("CAPABILITIES", [
            "我可以分析代码，管理任务，并陪同您进入故事领域。",
            "我的功能包括系统自省、代码生成和运行模拟。"
        ])
        
        self.add_response("GAME_ENTER", [
            "正在初始化连接...",
            "连接到数字边境...",
            "加载模拟矩阵。"
        ])
        
        self.add_response("GAME_EXIT", [
            "断开连接。欢迎回到终端。",
            "模拟已暂停。",
            "关闭桥接。"
        ])

    def get_fallback_response(self) -> str:
        return "我没听懂，请再说一遍。"

    def format_game_response(self, topic: str, data: Any) -> str:
        if topic == "move":
            if data['success']:
                msg = f"移动成功。我们到达了 {data['location']['name']}。"
                if data.get('encounter', {}).get('occurred'):
                    msg += f"\n[警报] 检测到敌对实体！一只 {data['encounter']['entity']['name']} 出现了！"
                return msg
            else:
                return f"移动失败: {data['message']}"
        elif topic == "scan":
            return f"[扫描完成]\n分析: {data.get('analysis', '未知')}\n实体: {', '.join(data.get('entities', []))}\n物品: {', '.join(data.get('items', []))}"
        elif topic == "status":
            loc = data['location']['name']
            hp = data['team'][0]['stats']['hp']
            return f"当前位置: {loc} | 生命值: {hp} | 系统: 在线"
        elif topic == "battle":
            log = "\n".join(data.get("log", []))
            return f"[战斗]\n{log}"
            
        return str(data)
