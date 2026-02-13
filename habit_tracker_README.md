# 🎯 Habit Tracker CLI

A beautiful command-line habit tracker with streak counters, visualizations, reminders, CSV export, and gamification elements!

![Habit Tracker Demo](https://img.shields.io/badge/cli-habit%20tracker-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)

## ✨ Features

- **🔥 Streak Counters** - Track current and longest streaks for each habit
- **📊 Visual Heatmaps** - ASCII calendar heatmaps showing completion patterns
- **⏰ Reminders** - Set daily reminder times for habits
- **📁 CSV Export** - Export all your data for analysis elsewhere
- **🎮 Gamification** - XP system, levels, and achievements to keep you motivated

## 🚀 Quick Start

```bash
# Add your first habit
./habit_tracker.py add "Exercise" --color green --target 30

# Mark it complete
./habit_tracker.py done "Exercise"

# See your progress
./habit_tracker.py list
./habit_tracker.py stats
```

## 📋 Commands

### Add a Habit
```bash
./habit_tracker.py add "Habit Name" [options]

Options:
  --color {red,green,yellow,blue,magenta,cyan}  Habit color (default: blue)
  --target INTEGER                              Target streak days (default: 7)
  --reminder HH:MM                              Daily reminder time

Examples:
  ./habit_tracker.py add "Exercise" --color green --target 30
  ./habit_tracker.py add "Read 30 min" --reminder 20:00
```

### Complete a Habit
```bash
./habit_tracker.py done "Habit Name" [--date YYYY-MM-DD]

Examples:
  ./habit_tracker.py done "Exercise"
  ./habit_tracker.py done "Exercise" --date 2024-01-15
```

### List Habits
```bash
./habit_tracker.py list
```
Shows all habits with current streaks and completion status.

### View Statistics
```bash
./habit_tracker.py stats [--habit "Habit Name"]
```
Displays detailed stats including:
- Current and longest streaks
- Total days completed
- 30-day completion rate
- ASCII heatmap calendar
- Progress bars toward targets

### View Achievements
```bash
./habit_tracker.py achievements
```

### Export to CSV
```bash
./habit_tracker.py export [--filename custom_name.csv]
```

### Delete a Habit
```bash
./habit_tracker.py delete "Habit Name"
```

## 🏆 Achievements

| Achievement | Description | Requirement |
|-------------|-------------|-------------|
| 🌱 First Step | Complete your first habit | 1 total day |
| 💪 Dedicated | Complete 30 total days | 30 total days |
| 💯 Century Club | Complete 100 total days | 100 total days |
| 🚀 Unstoppable | Complete 365 total days | 365 total days |
| 🔥 Week Warrior | Maintain a 7-day streak | 7-day streak |
| ⭐ Perfect Week | 7 days without missing | 7-day streak |
| ⚡ Month Master | Maintain a 30-day streak | 30-day streak |
| 👑 Habit Hero | Maintain a 100-day streak | 100-day streak |

## 📁 Data Storage

Habits are stored in:
- `~/.habit_tracker/habits.json` - Your habits and completion data
- `~/.habit_tracker/achievements.json` - Unlocked achievements

## 🎨 Example Output

```
╔══════════════════════════════════════════════════════════════╗
║                    📊 HABIT STATISTICS                       ║
╚══════════════════════════════════════════════════════════════╝

🎮 Level 3  •  XP: 245
   [████████████████░░░░] 45.0%

📌 Exercise ━━━━━━━━━━━━━━━━━━━━━━━
   🔥 Current Streak: 12 days
   🏆 Longest Streak: 15 days
   📅 Total Days: 45
   📈 30-Day Rate: 85.0%
   🎯 Target: 30 days
   [████████░░░░░░░░░░░░] 40.0%

Exercise ━━━━━━━━━━━━━━━━
     S M T W T F S
Sun  · · █ █ █ █ █ █
Mon  · █ █ █ █ █ █ █
Tue  · █ █ █ █ █ █ █
Wed  · █ █ █ █ █ █ █
Thu  · █ █ █ █ █ █ █
Fri  · █ █ █ █ █ █ █
Sat  · █ █ █ █ █ █ █

🏆 ACHIEVEMENT UNLOCKED: 🔥 Week Warrior
   Maintain a 7-day streak
```

## 💡 Tips

1. **Start Small** - Set achievable target streaks (7 days) and increase as you build momentum
2. **Use Colors** - Assign different colors to different types of habits
3. **Set Reminders** - Use `--reminder` to set daily nudges
4. **Export Regularly** - Back up your progress with CSV exports
5. **Check Stats** - Review your heatmaps to identify patterns

## 🔧 Requirements

- Python 3.8+
- No external dependencies (uses only standard library)

## 📄 License

MIT License - Feel free to use and modify!
