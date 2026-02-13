#!/usr/bin/env python3
"""
Habit Tracker CLI - Track daily habits with streaks, visualizations, and gamification!

Features:
- Track multiple habits with streak counters
- Visual calendar heatmaps in the terminal
- Reminders for incomplete habits
- CSV export for data portability
- Gamification with levels, achievements, and XP
"""

import json
import os
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse
import sys


@dataclass
class Habit:
    name: str
    created_at: str
    completed_dates: List[str]
    color: str = "blue"
    target_days: int = 7  # Target streak days
    reminder_time: Optional[str] = None  # Format: "HH:MM"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Habit":
        return cls(**data)


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    condition_type: str  # "streak", "total", "consistency"
    threshold: int
    unlocked_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


class HabitTracker:
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }
    
    ACHIEVEMENTS_DEF = [
        Achievement("first_step", "First Step", "Complete your first habit", "🌱", "total", 1),
        Achievement("week_warrior", "Week Warrior", "Maintain a 7-day streak", "🔥", "streak", 7),
        Achievement("month_master", "Month Master", "Maintain a 30-day streak", "⚡", "streak", 30),
        Achievement("century_club", "Century Club", "Complete 100 total days", "💯", "total", 100),
        Achievement("perfect_week", "Perfect Week", "7 days in a row without missing", "⭐", "streak", 7),
        Achievement("habit_hero", "Habit Hero", "Maintain a 100-day streak", "👑", "streak", 100),
        Achievement("dedicated", "Dedicated", "Complete 30 total days", "🎯", "total", 30),
        Achievement("unstoppable", "Unstoppable", "Complete 365 total days", "🚀", "total", 365),
    ]
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".habit_tracker"
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / "habits.json"
        self.achievements_file = self.data_dir / "achievements.json"
        self.habits: Dict[str, Habit] = {}
        self.unlocked_achievements: List[str] = []
        self.xp = 0
        self.level = 1
        self.load_data()
    
    def color(self, text: str, color: str) -> str:
        """Apply color to text."""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    
    def load_data(self):
        """Load habits and achievements from disk."""
        if self.data_file.exists():
            with open(self.data_file, "r") as f:
                data = json.load(f)
                self.habits = {
                    name: Habit.from_dict(h) 
                    for name, h in data.get("habits", {}).items()
                }
                self.xp = data.get("xp", 0)
                self.level = data.get("level", 1)
        
        if self.achievements_file.exists():
            with open(self.achievements_file, "r") as f:
                data = json.load(f)
                self.unlocked_achievements = data.get("unlocked", [])
    
    def save_data(self):
        """Save habits and achievements to disk."""
        data = {
            "habits": {name: h.to_dict() for name, h in self.habits.items()},
            "xp": self.xp,
            "level": self.level,
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
        
        with open(self.achievements_file, "w") as f:
            json.dump({"unlocked": self.unlocked_achievements}, f, indent=2)
    
    def calculate_streak(self, habit: Habit) -> int:
        """Calculate current streak for a habit."""
        if not habit.completed_dates:
            return 0
        
        dates = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in habit.completed_dates], reverse=True)
        today = datetime.now().date()
        
        streak = 0
        check_date = today
        
        # Check if completed today or yesterday (allowing for yesterday as grace)
        if dates and (today - dates[0]).days <= 1:
            for i, date in enumerate(dates):
                expected_date = today - timedelta(days=i)
                if date == expected_date or (i == 0 and (today - date).days <= 1):
                    streak += 1
                else:
                    break
        
        return streak
    
    def calculate_longest_streak(self, habit: Habit) -> int:
        """Calculate longest streak ever achieved."""
        if not habit.completed_dates:
            return 0
        
        dates = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in habit.completed_dates])
        if not dates:
            return 0
        
        longest = 1
        current = 1
        
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current += 1
                longest = max(longest, current)
            elif dates[i] != dates[i-1]:  # Skip duplicates
                current = 1
        
        return longest
    
    def get_completion_rate(self, habit: Habit, days: int = 30) -> float:
        """Calculate completion rate over last N days."""
        if not habit.completed_dates:
            return 0.0
        
        today = datetime.now().date()
        start_date = today - timedelta(days=days)
        
        completed_in_range = sum(
            1 for d in habit.completed_dates
            if start_date <= datetime.strptime(d, "%Y-%m-%d").date() <= today
        )
        
        return (completed_in_range / days) * 100
    
    def add_habit(self, name: str, color: str = "blue", target_days: int = 7, reminder: Optional[str] = None):
        """Add a new habit."""
        if name in self.habits:
            print(self.color(f"⚠️  Habit '{name}' already exists!", "yellow"))
            return False
        
        self.habits[name] = Habit(
            name=name,
            created_at=datetime.now().strftime("%Y-%m-%d"),
            completed_dates=[],
            color=color,
            target_days=target_days,
            reminder_time=reminder
        )
        self.save_data()
        print(self.color(f"✅ Added habit: {name}", "green"))
        return True
    
    def delete_habit(self, name: str):
        """Delete a habit."""
        if name not in self.habits:
            print(self.color(f"⚠️  Habit '{name}' not found!", "yellow"))
            return False
        
        del self.habits[name]
        self.save_data()
        print(self.color(f"🗑️  Deleted habit: {name}", "yellow"))
        return True
    
    def complete_habit(self, name: str, date: Optional[str] = None):
        """Mark a habit as complete for a date."""
        if name not in self.habits:
            print(self.color(f"⚠️  Habit '{name}' not found!", "yellow"))
            return False
        
        habit = self.habits[name]
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        
        if target_date in habit.completed_dates:
            print(self.color(f"ℹ️  Already completed '{name}' for {target_date}", "cyan"))
            return False
        
        habit.completed_dates.append(target_date)
        
        # Award XP (10 base + streak bonus)
        streak = self.calculate_streak(habit)
        xp_gain = 10 + min(streak, 10)  # Max 20 XP per completion
        self.xp += xp_gain
        
        # Level up check
        old_level = self.level
        self.level = (self.xp // 100) + 1
        
        self.save_data()
        
        # Check achievements
        self.check_achievements(habit)
        
        print(self.color(f"✅ Completed '{name}' for {target_date}", "green"))
        print(self.color(f"   🎮 +{xp_gain} XP (Streak: {streak + 1})", "cyan"))
        
        if self.level > old_level:
            print(self.color(f"   🆙 LEVEL UP! You are now level {self.level}!", "magenta"))
        
        return True
    
    def uncomplete_habit(self, name: str, date: Optional[str] = None):
        """Unmark a habit as complete for a date."""
        if name not in self.habits:
            print(self.color(f"⚠️  Habit '{name}' not found!", "yellow"))
            return False
        
        habit = self.habits[name]
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        
        if target_date not in habit.completed_dates:
            print(self.color(f"ℹ️  '{name}' was not completed for {target_date}", "cyan"))
            return False
        
        habit.completed_dates.remove(target_date)
        self.save_data()
        print(self.color(f"↩️  Uncompleted '{name}' for {target_date}", "yellow"))
        return True
    
    def check_achievements(self, habit: Habit):
        """Check and unlock achievements."""
        streak = self.calculate_streak(habit)
        total_days = len(habit.completed_dates)
        
        for achievement in self.ACHIEVEMENTS_DEF:
            if achievement.id in self.unlocked_achievements:
                continue
            
            should_unlock = False
            if achievement.condition_type == "streak" and streak >= achievement.threshold:
                should_unlock = True
            elif achievement.condition_type == "total" and total_days >= achievement.threshold:
                should_unlock = True
            
            if should_unlock:
                self.unlocked_achievements.append(achievement.id)
                print(self.color(
                    f"🏆 ACHIEVEMENT UNLOCKED: {achievement.icon} {achievement.name}\n"
                    f"   {achievement.description}", "yellow"
                ))
                # Bonus XP for achievements
                self.xp += 50
        
        self.save_data()
    
    def get_heatmap(self, habit: Habit, weeks: int = 12) -> str:
        """Generate an ASCII heatmap for a habit."""
        today = datetime.now().date()
        completed_set = set(habit.completed_dates)
        
        lines = []
        lines.append(f"{self.color(habit.name, habit.color)} {self.color('━' * 20, 'white')}")
        
        # Day labels
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        lines.append("     " + " ".join(d[0] for d in day_names))
        
        # Calculate start date (align to Sunday)
        start_date = today - timedelta(weeks=weeks, days=today.weekday() + 1)
        
        for day_offset in range(7):
            row = []
            for week in range(weeks + 1):
                date = start_date + timedelta(weeks=week, days=day_offset)
                date_str = date.strftime("%Y-%m-%d")
                
                if date > today:
                    row.append(" ")
                elif date_str in completed_set:
                    # Different intensity based on recency
                    days_ago = (today - date).days
                    if days_ago <= 7:
                        row.append(self.color("█", "green"))
                    elif days_ago <= 14:
                        row.append(self.color("▓", "green"))
                    else:
                        row.append(self.color("░", "green"))
                else:
                    row.append(self.color("·", "white"))
            
            day_label = day_names[day_offset][:3]
            lines.append(f"{day_label}  " + " ".join(row))
        
        return "\n".join(lines)
    
    def get_progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """Generate a progress bar."""
        filled = int((current / total) * width) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        percentage = (current / total) * 100 if total > 0 else 0
        return f"[{self.color(bar, 'cyan')}] {percentage:.1f}%"
    
    def show_stats(self, habit_name: Optional[str] = None):
        """Display statistics for habits."""
        if not self.habits:
            print(self.color("📭 No habits tracked yet! Add one with: habit add <name>", "yellow"))
            return
        
        habits_to_show = [habit_name] if habit_name else list(self.habits.keys())
        
        print()
        print(self.color("╔══════════════════════════════════════════════════════════════╗", "magenta"))
        print(self.color("║                    📊 HABIT STATISTICS                       ║", "magenta"))
        print(self.color("╚══════════════════════════════════════════════════════════════╝", "magenta"))
        print()
        
        # Player stats
        next_level_xp = self.level * 100
        current_level_xp = (self.level - 1) * 100
        level_progress = self.xp - current_level_xp
        
        print(self.color(f"🎮 Level {self.level}  •  XP: {self.xp}", "cyan"))
        print(f"   {self.get_progress_bar(level_progress, 100)}")
        print()
        
        for name in habits_to_show:
            if name not in self.habits:
                print(self.color(f"⚠️  Habit '{name}' not found!", "yellow"))
                continue
            
            habit = self.habits[name]
            streak = self.calculate_streak(habit)
            longest = self.calculate_longest_streak(habit)
            total = len(habit.completed_dates)
            rate_30 = self.get_completion_rate(habit, 30)
            
            print(self.color(f"📌 {name}", habit.color) + self.color(" ━━━━━━━━━━━━━━━━━━━━━━━", "white"))
            print(f"   🔥 Current Streak: {streak} days")
            print(f"   🏆 Longest Streak: {longest} days")
            print(f"   📅 Total Days: {total}")
            print(f"   📈 30-Day Rate: {rate_30:.1f}%")
            print(f"   🎯 Target: {habit.target_days} days")
            print(f"   {self.get_progress_bar(streak, habit.target_days)}")
            print()
            print(self.get_heatmap(habit))
            print()
    
    def show_list(self):
        """List all habits with quick stats."""
        if not self.habits:
            print(self.color("📭 No habits tracked yet! Add one with: habit add <name>", "yellow"))
            return
        
        print()
        print(self.color("╔══════════════════════════════════════════════════════════════╗", "magenta"))
        print(self.color("║                    📋 YOUR HABITS                            ║", "magenta"))
        print(self.color("╚══════════════════════════════════════════════════════════════╝", "magenta"))
        print()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        for name, habit in self.habits.items():
            streak = self.calculate_streak(habit)
            completed_today = today in habit.completed_dates
            
            status = self.color("✅", "green") if completed_today else self.color("⬜", "white")
            streak_fire = "🔥" * min(streak // 7 + 1, 5) if streak > 0 else ""
            
            print(f"{status} {self.color(name, habit.color)} {streak_fire}")
            print(f"   Streak: {streak} days  •  Total: {len(habit.completed_dates)} days")
            print()
    
    def show_achievements(self):
        """Display unlocked achievements."""
        print()
        print(self.color("╔══════════════════════════════════════════════════════════════╗", "magenta"))
        print(self.color("║                  🏆 ACHIEVEMENTS                             ║", "magenta"))
        print(self.color("╚══════════════════════════════════════════════════════════════╝", "magenta"))
        print()
        
        if not self.unlocked_achievements:
            print(self.color("No achievements unlocked yet. Keep going! 💪", "yellow"))
            return
        
        for achievement in self.ACHIEVEMENTS_DEF:
            unlocked = achievement.id in self.unlocked_achievements
            icon = achievement.icon if unlocked else "🔒"
            name = achievement.name if unlocked else "???"
            desc = achievement.description if unlocked else "Keep trying to unlock!"
            status = self.color("UNLOCKED", "green") if unlocked else self.color("LOCKED", "white")
            
            print(f"{icon} {name}")
            print(f"   {desc}")
            print(f"   {status}")
            print()
    
    def check_reminders(self):
        """Check for due reminders."""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")
        
        reminders = []
        for name, habit in self.habits.items():
            if habit.reminder_time and today not in habit.completed_dates:
                # Simple check - if reminder time has passed
                if habit.reminder_time <= current_time:
                    reminders.append(name)
        
        if reminders:
            print()
            print(self.color("🔔 REMINDERS:", "yellow"))
            for name in reminders:
                print(self.color(f"   ⏰ Don't forget to complete: {name}", "cyan"))
            print()
    
    def export_csv(self, filename: Optional[str] = None):
        """Export habits data to CSV."""
        if not filename:
            filename = f"habits_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Habit Name", "Date", "Status", "Streak", "Total Completed"
            ])
            
            for name, habit in self.habits.items():
                # Write each completed date
                for date in sorted(habit.completed_dates):
                    streak_at_date = self.calculate_streak_at_date(habit, date)
                    writer.writerow([
                        name,
                        date,
                        "Completed",
                        streak_at_date,
                        len(habit.completed_dates)
                    ])
        
        print(self.color(f"📁 Exported to: {filename}", "green"))
        return filename
    
    def calculate_streak_at_date(self, habit: Habit, target_date_str: str) -> int:
        """Calculate streak at a specific date."""
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        dates = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in habit.completed_dates])
        
        if target_date not in dates:
            return 0
        
        streak = 1
        target_idx = dates.index(target_date)
        
        # Count backwards
        for i in range(target_idx - 1, -1, -1):
            if (dates[i + 1] - dates[i]).days == 1:
                streak += 1
            else:
                break
        
        return streak


def main():
    parser = argparse.ArgumentParser(
        description="Habit Tracker CLI - Gamify your self-improvement!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add "Exercise" --color green --target 30
  %(prog)s done "Exercise"
  %(prog)s list
  %(prog)s stats
  %(prog)s export
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add habit
    add_parser = subparsers.add_parser("add", help="Add a new habit")
    add_parser.add_argument("name", help="Habit name")
    add_parser.add_argument("--color", choices=["red", "green", "yellow", "blue", "magenta", "cyan"],
                           default="blue", help="Habit color")
    add_parser.add_argument("--target", type=int, default=7, help="Target streak days")
    add_parser.add_argument("--reminder", help="Reminder time (HH:MM)")
    
    # Delete habit
    del_parser = subparsers.add_parser("delete", help="Delete a habit")
    del_parser.add_argument("name", help="Habit name")
    
    # Complete habit
    done_parser = subparsers.add_parser("done", help="Mark habit as complete")
    done_parser.add_argument("name", help="Habit name")
    done_parser.add_argument("--date", help="Date to mark (YYYY-MM-DD, default: today)")
    
    # Uncomplete habit
    undo_parser = subparsers.add_parser("undo", help="Unmark habit as complete")
    undo_parser.add_argument("name", help="Habit name")
    undo_parser.add_argument("--date", help="Date to unmark (YYYY-MM-DD, default: today)")
    
    # List habits
    subparsers.add_parser("list", help="List all habits")
    
    # Show stats
    stats_parser = subparsers.add_parser("stats", help="Show detailed statistics")
    stats_parser.add_argument("--habit", help="Show stats for specific habit")
    
    # Show achievements
    subparsers.add_parser("achievements", help="Show unlocked achievements")
    
    # Export to CSV
    export_parser = subparsers.add_parser("export", help="Export data to CSV")
    export_parser.add_argument("--filename", help="Output filename")
    
    # Check reminders
    subparsers.add_parser("reminders", help="Check pending reminders")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    tracker = HabitTracker()
    
    if args.command == "add":
        tracker.add_habit(args.name, args.color, args.target, args.reminder)
    
    elif args.command == "delete":
        tracker.delete_habit(args.name)
    
    elif args.command == "done":
        tracker.complete_habit(args.name, args.date)
    
    elif args.command == "undo":
        tracker.uncomplete_habit(args.name, args.date)
    
    elif args.command == "list":
        tracker.show_list()
    
    elif args.command == "stats":
        tracker.show_stats(args.habit)
    
    elif args.command == "achievements":
        tracker.show_achievements()
    
    elif args.command == "export":
        tracker.export_csv(args.filename)
    
    elif args.command == "reminders":
        tracker.check_reminders()


if __name__ == "__main__":
    main()
