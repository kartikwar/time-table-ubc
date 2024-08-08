import pandas as pd
import numpy as np


def split_meeting_patterns(meeting_pattern):
    # Split the date range first
    date_range, rest = meeting_pattern.split(' | ', 1)
    start_date, end_date = date_range.split(' - ')
    
    # Split the remaining part into days, time, and location
    days, time, location = rest.split(' | ')
    
    return pd.Series([start_date, end_date, days, time, location])



def refine_schedule(schedule_df):
    # Apply the function to split the Meeting Patterns column
    split_columns = schedule_df['Meeting Patterns'].apply(split_meeting_patterns)

    # Assign the split columns to the dataframe with the appropriate column names
    schedule_df[['Start Date', 'End Date', 'Days', 'Time', 'Location']] = split_columns

    #Drop the original Meeting Patterns column as it's now split into individual components
    # schedule_df = schedule_df.drop(columns=['Meeting Patterns'])

    schedule_df_sorted = schedule_df.sort_values(by='Start Date')

    # Display the updated dataframe
    print(schedule_df.head())

    return schedule_df_sorted


# Function to create the timetable for each group
def create_timetable(df):
    # Create a new dataframe with days of the week as rows and time slots as columns
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    times = sorted(df['Time'].unique())
    timetable = pd.DataFrame(index=days, columns=times)
    
    for _, row in df.iterrows():
        for day in row['Days'].split():
            if day in timetable.index:
                timetable.at[day, row['Time']] = f"{row['Course Listing']}, {row['Location']}, {row['Instructional Format']}"
    
    # Remove any columns and rows that are completely empty
    timetable = timetable.dropna(axis=1, how='all').dropna(axis=0, how='all')
    
    return timetable


# Update the save_timetable function to handle the corrected datetime format
def save_timetable(timetable, start_date, end_date):
    # Convert the dates to datetime format if they aren't already
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    
    file_name = f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}.csv"
    file_path = f"{file_name}"
    timetable.to_csv(file_path)
    return file_path

def get_time_tables(schedule_df_sorted):
    schedule_df_sorted['Start Date'] = pd.to_datetime(schedule_df_sorted['Start Date'])
    schedule_df_sorted['End Date'] = pd.to_datetime(schedule_df_sorted['End Date'])
    # Calculate the difference in days between consecutive rows
    schedule_df_sorted['Date Difference'] = schedule_df_sorted['Start Date'].diff().dt.days

    # Create a 'Group' column to differentiate between different timetables
    schedule_df_sorted['Group'] = (schedule_df_sorted['Date Difference'] > 5).cumsum()

    # Drop the 'Date Difference' column as it's no longer needed
    schedule_df_sorted = schedule_df_sorted.drop(columns=['Date Difference'])

    # Split the data into separate timetables based on the 'Group' column
    grouped_timelines = [group for _, group in schedule_df_sorted.groupby('Group')]

    # timetables = [create_timetable(group) for group in grouped_timelines]

    # Save all timetables with the specified file names
    saved_files = []
    for group in grouped_timelines:
        start_date = group['Start Date'].min()
        end_date = group['End Date'].max()
        timetable = create_timetable(group)
        saved_files.append(save_timetable(timetable, start_date, end_date))

    return saved_files



if __name__ == '__main__':
    file_path = 'Current_Schedule.csv'
    df = pd.read_csv(file_path)
    df = refine_schedule(df)
    # df.to_csv('schedule_changed.csv')
    time_tables = get_time_tables(df)
    print(df.head())