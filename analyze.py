# Analyze prayer times from a csv file

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.dates as mdates

CSV_FILE = Path("Aachen_2025.csv")
    #    #  Day     Gregorian Date   Hijri Date   Fajr   Shuruq   Zuhr   Assr    Maghrib  Ishaa
    # 0  1  Wed     2025-01-01       1446/7/1     06:37  08:33    12:45  14:26   16:46    18:36
    # 1  2  Thu     2025-01-02       1446/7/2     06:37  08:33    12:45  14:27   16:47    18:36
    # ...

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

def calculate_prayer_durations(df):
    """Calculate durations between prayer times and add them as new columns"""
    # Duration from midnight to Fajr
    df['duration_midnight_to_fajr'] = df['Fajr_min']
    
    # Duration between Fajr and Shuruq
    df['duration_fajr_to_shuruq'] = df['Shuruq_min'] - df['Fajr_min']
    
    # Duration between Shuruq and Zuhr
    df['duration_shuruq_to_zuhr'] = df['Zuhr_min'] - df['Shuruq_min']
    
    # Duration between Zuhr and Asr
    df['duration_zuhr_to_asr'] = df['Assr_min'] - df['Zuhr_min']
    
    # Duration between Asr and Maghrib
    df['duration_asr_to_maghrib'] = df['Maghrib_min'] - df['Assr_min']
    
    # Duration between Maghrib and Ishaa
    df['duration_maghrib_to_ishaa'] = df['Ishaa_min'] - df['Maghrib_min']
    
    # Duration from Ishaa to midnight (next day)
    df['duration_ishaa_to_midnight'] = (24 * 60) - df['Ishaa_min']
    
    # Verify the total is 24 hours (1440 minutes) for each day
    total_minutes = (df['duration_midnight_to_fajr'] + 
                    df['duration_fajr_to_shuruq'] + 
                    df['duration_shuruq_to_zuhr'] + 
                    df['duration_zuhr_to_asr'] + 
                    df['duration_asr_to_maghrib'] + 
                    df['duration_maghrib_to_ishaa'] + 
                    df['duration_ishaa_to_midnight'])
    
    assert (total_minutes == 1440).all(), "Error: Total duration is not 24 hours for some days"
    
    return df

def graph_prayer_durations(df):
    """Create a stacked bar graph showing durations between prayer times"""
    # Convert Gregorian Date to datetime and set as index
    df["Gregorian Date"] = pd.to_datetime(df["Gregorian Date"])
    
    # Duration columns in order from first to last in the day
    duration_columns = [
        'duration_midnight_to_fajr',
        'duration_fajr_to_shuruq',
        'duration_shuruq_to_zuhr',
        'duration_zuhr_to_asr',
        'duration_asr_to_maghrib',
        'duration_maghrib_to_ishaa',
        'duration_ishaa_to_midnight'
    ]
    
    # Labels for the legend
    labels = [
        'Midnight to Fajr',
        'Fajr to Shuruq',
        'Shuruq to Zuhr',
        'Zuhr to Asr',
        'Asr to Maghrib',
        'Maghrib to Ishaa',
        'Ishaa to Midnight'
    ]
    
    # Colors for each segment (from night to day and back to night)
    colors = [
        '#1a1a4a',  # Dark blue (Midnight to Fajr) - slightly lighter and more saturated
        '#ff6b35',  # Sunrise orange (Fajr to Shuruq) - sunset color
        '#7cb342',  # Light green (Shuruq to Zuhr) - changed to green
        '#a5b4fc',  # Lighter blue-purple (Zuhr to Asr) - made lighter
        '#9575cd',  # More saturated purple (Asr to Maghrib)
        '#ff7e5f',  # Sunset orange-red (Maghrib to Ishaa) - sunset color
        '#0a0a30'   # Dark blue (Ishaa to Midnight) - slightly lighter and more saturated
    ]
    
    # Create the figure and axis with larger size
    plt.figure(figsize=(15, 8))
    
    # Create the stacked bar chart with custom colors
    bottom = None
    for i, (col, color) in enumerate(zip(duration_columns, colors)):
        if bottom is None:
            # First segment starts at 0
            plt.bar(df["Gregorian Date"], df[col] / 60, 
                   color=color, label=labels[i], width=1)
            bottom = df[col]
        else:
            plt.bar(df["Gregorian Date"], df[col] / 60, 
                   bottom=bottom / 60, color=color, 
                   label=labels[i], width=1)
            bottom += df[col]
    
    # Format y-axis to show hours:minutes
    from matplotlib.ticker import FuncFormatter
    def hours_minutes(x, pos):
        hours = int(x)
        minutes = int((x * 60) % 60)
        return f"{hours:02d}:{minutes:02d}"
    
    # Get current axis and set formatter
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FuncFormatter(hours_minutes))
    
    # Set y-axis limits and ticks
    plt.ylim(0, 24)
    y_ticks = range(0, 25, 2)  # Major ticks every 2 hours
    plt.yticks(y_ticks, [f"{h:02d}:00" for h in y_ticks])
    
    # Add minor ticks for every hour
    ax.set_yticks(range(0, 25, 1), minor=True)
    
    # Format the plot
    title = CSV_FILE.stem.replace('_', ' ') + ' - Daily Prayer Time Durations'
    plt.title(title, pad=20)
    plt.xlabel('Date')
    plt.ylabel('Time of Day (HH:MM)')
    
    # Customize legend
    legend = plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Customize grid lines - darker and more visible
    plt.grid(True, which='both', alpha=0.5, color='#666666', linestyle='-', linewidth=0.5)
    
    # Add vertical grid lines for each month
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.grid(True, which='major', axis='x', linestyle='--', alpha=0.7, color='#999999')
    
    # Adjust layout to add some padding for better visibility
    plt.subplots_adjust(bottom=0.12, top=0.9, right=0.8, left=0.1)
    
    # Add some spacing between bars
    plt.margins(x=0.02)
    
    # Save the figure before showing it
    output_filename = f"{CSV_FILE.stem}_year_graph.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Graph saved as {output_filename}")
    
    plt.tight_layout()
    plt.show()

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
    
    # Calculate durations between prayer times
    df = calculate_prayer_durations(df)
    
    print("First few rows with duration columns:")
    print(df[['Gregorian Date', 'Fajr', 'Fajr_min', 'duration_midnight_to_fajr']].head())
    
    # Plot Fajr times
    # graph_all_farj_times(df)
    
    # Plot prayer time durations
    graph_prayer_durations(df)

if __name__ == "__main__":
    main()
