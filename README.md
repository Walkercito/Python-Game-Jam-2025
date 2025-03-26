# Awaking - PyGame Jam 2025 Entry

![Main Menu of Awaking](https://not-yet.com)  
*In a world that never stops, what if someone dared to pause..?*

## 👥 Team: Qva Team
- **Programmer**: Walkercito  
- **Artist**: CanIIAweekee  

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- pygame-ce 2.5.3
- pytmx 3.32
- asyncio 
- [UV](https://docs.astral.sh/uv/) (Ultra-fast Python package installer)

### Quick Install UV
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Getting Started
1. Clone the repo:
```bash
git clone https://github.com/Walkercito/Python-Game-Jam-2025
   cd Python-Game-Jam-2025
```
2. Install dependencies
```bash
uv sync
```
3. Run the game
```
uv run main.py
```

> [!NOTE]
> **Pre-built Executable Available**  
> You can download a Windows executable from our [Releases section](https://github.com/Walkercito/Python-Game-Jam-2025/releases).  
>   
> - Compiled with `PyInstaller` (may trigger false Windows Defender alerts)  
> - For complete safety:  
>   • Run from source
>    ```bash
>    uv run main.py
>    ``` 
>   • Or [build it yourself](https://pyinstaller.readthedocs.io/)

---
## 🎮 How to Play

> **Awaking** is a 5-minute minimalist experience where you play as a character who must choose between breaking the current (helping others break free from addiction) or going with the flow (accepting the status quo). Your decisions determine which of the two alternate endings you'll reach, reflecting the game jam's *downstream* theme through simple yet meaningful narrative.

- [W/A/S/D] -> To move in four directions
-    [E]    -> To interact with when the indicator above and NPC appears
-   [ESC]   -> To open setting inside the game
-   [Mouse] -> Only for the main menu and settings

### Objective  

**Two bars track your struggle in the bottom-left corner:**  
- **Influence (Blue)**: Your power to change minds  
- **Energy (Golden)**: The stamina to keep fighting  

The city flows like a river of glowing screens. You move against the current, offering weathered books to strangers drowning in digital light. Some shrug you off—their rejection drains your resolve. Others hesitate, and in that moment, you pour your energy into persuasion. Even standing still has consequences; the tide erodes your will differently when you choose not to act.  

Three types of people drift through this neon stream: the willing, the resistant, and those too far gone. Learn their rhythms—your success depends on reading the subtle currents in their eyes.  

*(Mechanically: Each NPC interaction dynamically affects your Influence and Energy bars. Manage both resources carefully to reach the ending you desire.)*  

---

## Licence 
MIT
