from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
import random
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text


@dataclass
class WeatherData:
    temperature: float
    humidity: float
    pressure: float
    timestamp: datetime = datetime.now()


class Randy:
    """
    An enthusiastic personality for the weather station.
    Note: This character may resemble Randy from South Park, but they are not related.
    """

    GREETINGS = [
        "Oh hey there! Welcome to the weather station!",
        "Ya ya ya, I am the weather lord ya ya ya!",
        "Hey hey! Ready for some weather? I'm so excited I could take my shirt off!",
        "Welcome to our Weather Station! I'm feeling pretty scientific today!",
    ]

    WEATHER_COMMENTS = [
        "Oh my god, this is like, the most perfect weather I've ever seen! Honey! Honey, come look at this!",
        "I'm getting a clue about the weather... Oh yeah, big clue!",
        "The temperature is giving me such a raging clue right now!",
        "This is better than that time I was a Food Network star!",
        "Just gonna get a little bit of weather, son. Tell Mom it's okay.",
    ]

    FAREWELL = [
        "I'm out! Gotta go fight some other weather enthusiasts!",
        "My wife is calling, gotta run!",
        "Time to go do some 'research' at the local farm!",
        "My son needs me for something probably not stupid at all!",
    ]


class WeatherStation:
    def __init__(self, *, name: str = "South Park Weather Station"):
        self.name: str = name
        self.randy: Randy = Randy()
        self.console: Console = Console()
        self.weather_data: Optional[WeatherData] = None

    def _generate_mock_weather(self) -> WeatherData:
        """Generate mock weather data"""
        return WeatherData(
            temperature=random.uniform(-10, 30),
            humidity=random.uniform(30, 90),
            pressure=random.uniform(980, 1020),
        )

    def _format_weather_panel(self, weather: WeatherData) -> Panel:
        """Format weather data into a Rich panel"""
        weather_text = Text()
        weather_text.append(
            f"Temperature: {weather.temperature:.1f}°C\n", style="bold cyan"
        )
        weather_text.append(f"Humidity: {weather.humidity:.1f}%\n", style="bold blue")
        weather_text.append(
            f"Pressure: {weather.pressure:.1f} hPa\n", style="bold magenta"
        )
        weather_text.append(
            f"\nTimestamp: {weather.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            style="italic",
        )

        return Panel(
            weather_text,
            title="[bold yellow]Current Weather Conditions[/]",
            border_style="green",
        )

    def start(self) -> None:
        """Start the weather station interface"""
        self.console.clear()
        self.console.print(
            Panel(random.choice(self.randy.GREETINGS), style="bold yellow")
        )

        while True:
            command = Prompt.ask(
                "\n[bold green]What would you like to know about the weather?[/]\n"
                "[dim](Type 'help' for commands, 'exit' to quit)[/]"
            ).lower()

            if command == "exit":
                self.console.print(
                    Panel(random.choice(self.randy.FAREWELL), style="bold yellow")
                )
                break

            elif command == "help":
                self.console.print(
                    Panel(
                        "Available commands:\n"
                        "- weather: Get current weather conditions\n"
                        "- comment: Get Randy's thoughts on the weather\n"
                        "- exit: Exit the weather station\n"
                        "- help: Show this help message",
                        title="[bold]Commands[/]",
                        border_style="blue",
                    )
                )

            elif command == "weather":
                self.weather_data = self._generate_mock_weather()
                self.console.print(self._format_weather_panel(self.weather_data))

            elif command == "comment":
                if self.weather_data is None:
                    self.console.print("[yellow]I need to check the weather first![/]")
                else:
                    self.console.print(
                        Panel(
                            random.choice(self.randy.WEATHER_COMMENTS),
                            style="bold yellow",
                        )
                    )

            else:
                self.console.print(
                    "[red]I don't know what that means! Try 'help' for commands.[/]"
                )
