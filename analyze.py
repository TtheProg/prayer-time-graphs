# Analyze prayer times from a csv file

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def time_to_minutes(time_str):
    """Convert time string in format HH:MM to minutes since midnight"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def add_minute_columns(df):
    """Add minute columns for each prayer time"""
    prayer_columns = ['Fajr', 'Shuruq', 'Zuhr', 'Assr', 'Maghrib', 'Ishaa']
    for col in prayer_columns:
        df[f'{col}_min'] = df[col].apply(time_to_minutes)
    return df

CSV_FILE = Path("Aachen.csv")
    #    #  Day     Gregorian Date   Hijri Date   Fajr   Shuruq   Zuhr   Assr    Maghrib  Ishaa
    # 0  1  Wed     2025-01-01       1446/7/1     06:37  08:33    12:45  14:26   16:46    18:36
    # 1  2  Thu     2025-01-02       1446/7/2     06:37  08:33    12:45  14:27   16:47    18:36
    # ...

def graph_all_farj_times(df):
    # Convert Gregorian Date to datetime
    df["Gregorian Date"] = pd.to_datetime(df["Gregorian Date"])
    
    # Plot using the minute values
    plt.figure(figsize=(12, 6))
    plt.plot(df["Gregorian Date"], df["Fajr_min"] / 60)  # Convert back to hours for y-axis
    
    # Format y-axis to show hours:minutes
    from matplotlib.ticker import FuncFormatter
    def hours_formatter(x, pos):
        hours = int(x)
        minutes = int((x * 60) % 60)
        return f"{hours:02d}:{minutes:02d}"
    
    plt.gca().yaxis.set_major_formatter(FuncFormatter(hours_formatter))
    
    plt.title("Fajr Prayer Times")
    plt.xlabel("Date")
    plt.ylabel("Time of Day")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    # Load the data
    df = pd.read_csv(CSV_FILE)
    
    # Add minute columns for all prayer times
    df = add_minute_columns(df)
    
    print("First few rows with minute columns:")
    print(df[['Gregorian Date', 'Fajr', 'Fajr_min']].head())
    
    # Plot Fajr times
    graph_all_farj_times(df)

if __name__ == "__main__":
    main()
