from dataclasses import dataclass
from drafter import *

INTENSITY_OPTIONS = ["Low", "Medium", "High"]

set_site_information(
    author="Devin Karadagli",
    description="A simple workout log. Add workouts, view your history, and track your progress toward a weekly goal.",
    sources=["Official Drafter documentation only"],
    planning=["Devin Karadagli - Final Project 1_ Design.pdf"],
    links=["https://github.com/devkara-udel/workout-log-website"]
)
hide_debug_information()
set_website_title("Workout Log")
set_website_framed(False)


@dataclass
class Workout:
    exercise: str
    minutes: int
    intensity: str
    completed: bool


@dataclass
class State:
    workouts: list[Workout]
    weekly_goal_minutes: int
    total_minutes: int
    message: str


def parse_positive_int(text: str) -> int:
    """Convert text to a positive whole number, or return 0 if it is not valid."""
    cleaned = text.strip()
    if cleaned.isdigit():
        return int(cleaned)
    return 0


def count_high_intensity(workouts: list[Workout]) -> int:
    """Count how many workouts in the list have High intensity."""
    count = 0
    for workout in workouts:
        if workout.intensity == "High":
            count += 1
    return count


def minutes_remaining(state: State) -> int:
    """Return how many minutes are left to reach the weekly goal, never below zero."""
    remaining = state.weekly_goal_minutes - state.total_minutes
    if remaining < 0:
        return 0
    return remaining


def take_message(state: State) -> str:
    """Return the current message and clear it so it only shows once."""
    message = state.message
    state.message = ""
    return message


def goal_message(state: State) -> str:
    """Describe the user's progress toward the weekly goal."""
    remaining = minutes_remaining(state)
    if remaining == 0:
        return "Congratulations, you have reached your weekly goal!"
    return f"Keep going, you have {remaining} minutes left to reach your goal!"


@route
def index(state: State) -> Page:
    """Show the home page with goal progress and links to every other page."""
    return Page(state, [
        Header("Workout Log", 1),
        HorizontalRule(),
        "Welcome, track your workouts and work toward your weekly goal.",
        LineBreak(),
        LineBreak(),
        f"Your weekly goal is {state.weekly_goal_minutes} minutes.",
        LineBreak(),
        f"So far, you have logged {state.total_minutes} minutes.",
        LineBreak(),
        goal_message(state),
        LineBreak(),
        LineBreak(),
        take_message(state),
        HorizontalRule(),
        Button("Log a Workout", log_workout_page),
        LineBreak(),
        Button("View History", history),
        LineBreak(),
        Button("View Stats", stats),
        LineBreak(),
        Button("Set Weekly Goal", goal_page)
    ])


@route
def log_workout_page(state: State) -> Page:
    """Show the form for logging a new workout."""
    return Page(state, [
        Header("Log a Workout", 1),
        HorizontalRule(),
        take_message(state),
        LineBreak(),
        LineBreak(),
        "What exercise did you do?",
        LineBreak(),
        TextBox("exercise"),
        LineBreak(),
        LineBreak(),
        "How many minutes did you work out?",
        LineBreak(),
        TextBox("minutes"),
        LineBreak(),
        LineBreak(),
        "How intense was the workout?",
        LineBreak(),
        SelectBox("intensity", INTENSITY_OPTIONS, "Medium"),
        LineBreak(),
        LineBreak(),
        "Did you finish the workout?",
        LineBreak(),
        CheckBox("completed"),
        HorizontalRule(),
        Button("Save Workout", add_workout),
        LineBreak(),
        Button("Cancel", index)
    ])


@route
def add_workout(state: State, exercise: str, minutes: str, intensity: str, completed: bool) -> Page:
    """Validate the form, save a new Workout to the state, and show the history page."""
    minutes_value = parse_positive_int(minutes)
    clean_exercise = exercise.strip()
    if clean_exercise == "" or minutes_value == 0:
        state.message = "Please enter an exercise name, and enter the minutes as a positive whole number."
        return log_workout_page(state)
    state.workouts.append(Workout(clean_exercise, minutes_value, intensity, completed))
    state.total_minutes += minutes_value
    state.message = f"{clean_exercise} was added to your history, nice work!"
    return history(state)


@route
def history(state: State) -> Page:
    """Show every saved workout, or a notice if there are none yet."""
    if len(state.workouts) == 0:
        return Page(state, [
            Header("Workout History", 1),
            HorizontalRule(),
            "No workouts yet, log your first one to get started.",
            HorizontalRule(),
            Button("Back to Home", index)
        ])
    items = []
    for workout in state.workouts:
        status = "finished" if workout.completed else "not finished"
        items.append(f"{workout.exercise}, {workout.minutes} minutes, {workout.intensity} intensity, {status}")
    return Page(state, [
        Header("Workout History", 1),
        HorizontalRule(),
        take_message(state),
        BulletedList(items),
        HorizontalRule(),
        Button("Back to Home", index)
    ])


@route
def stats(state: State) -> Page:
    """Show total minutes, the high intensity count, and goal progress."""
    high_count = count_high_intensity(state.workouts)
    return Page(state, [
        Header("Your Stats", 1),
        HorizontalRule(),
        f"You have logged {state.total_minutes} minutes in total.",
        LineBreak(),
        f"You have logged {high_count} high intensity workouts.",
        LineBreak(),
        f"Your weekly goal is {state.weekly_goal_minutes} minutes.",
        LineBreak(),
        goal_message(state),
        HorizontalRule(),
        Button("Back to Home", index)
    ])


@route
def goal_page(state: State) -> Page:
    """Show the form for changing the weekly goal."""
    return Page(state, [
        Header("Set Your Weekly Goal", 1),
        HorizontalRule(),
        take_message(state),
        LineBreak(),
        LineBreak(),
        "How many minutes do you want to work out each week?",
        LineBreak(),
        TextBox("goal", str(state.weekly_goal_minutes)),
        HorizontalRule(),
        Button("Save Goal", save_goal),
        LineBreak(),
        Button("Cancel", index)
    ])


@route
def save_goal(state: State, goal: str) -> Page:
    """Validate the new goal, save it to the state, and return to the home page."""
    goal_value = parse_positive_int(goal)
    if goal_value == 0:
        state.message = "Please enter the goal as a positive whole number, such as 180."
        return goal_page(state)
    state.weekly_goal_minutes = goal_value
    state.message = "Your weekly goal has been updated, keep it up!"
    return index(state)


start_server(State([], 180, 0, ""))
