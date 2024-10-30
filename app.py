import pandas as pd
import streamlit as st

url = 'https://docs.google.com/spreadsheets/d/1pOxce5luIYRygXP90dh01-HdXaW2-9i4wkGyK3ycYIo/export?format=csv&gid=20815831'

df = pd.read_csv(url)


# Conver Runners Name to lower Case and strip whitespace
df['Student Name'] = df['Student Name'].str.lower().str.strip()
# Make date time correct format
df['Timestamp'] = pd.to_datetime(df['Timestamp'],dayfirst=True)
# Create Simple Date Column for Grouping
df['Date'] = df['Timestamp'].dt.date
df['Date'] = pd.to_datetime(df['Date'])
df['Room Number'] = df['Room Number'].str.lower().str.strip()
df['Room Number'] = df['Room Number'].str.replace(r'\broom\b\s*', '', regex=True)
df['Room Number'] = df['Room Number'].str.replace('kindy c','kindy')
#df['Student Name'] = df['Student Name'].str.replace(r'\lachlan s \b\s*', 'lachlan sucksmith',regex=True)
df = df.drop(labels=['Laps Completed (Sprints / Laps)','Timestamp'],axis=1)

# Sidebar Filters
st.sidebar.header('Filter Data')
view = st.sidebar.selectbox('View Stats By', ['Student Name','Date'])

# Main area
st.title('Running Club Stats')

if view == 'Date':
    # Group by Date to show the total number of runs
    runs_per_day = df.groupby('Date')['Student Name'].count().reset_index()
    runs_per_day.columns = ['Date', 'Total Runs']

    # Format the Date column to YYYY-MM-DD
    runs_per_day['Date'] = runs_per_day['Date'].dt.strftime('%Y-%m-%d')

    st.subheader('Total Runs by Date')
    st.table(runs_per_day)

    # Date-specific filter
    date_options = df['Date'].dt.strftime('%Y-%m-%d').unique()
    selected_date = st.selectbox('Select a Date', date_options)

    # Filter data based on selected date
    filtered_data = df[df['Date'].dt.strftime('%Y-%m-%d') == selected_date]
    st.subheader(f'Runners on {selected_date}')
    st.table(filtered_data)

elif view == 'Student Name':
    # Group by Student Name, Year, and Room Number to count the number of days each student ran
    top_runners = (
        df.groupby(['Student Name', 'Year', 'Room Number'])
        .size()
        .reset_index(name='Days Run')
        .sort_values(by='Days Run', ascending=False)
    )

    # Inline filter using a selectbox for Year
    year_options = ['All'] + df['Year'].unique().tolist()  # Add 'All' option to view all years
    selected_year = st.selectbox('Select Year', year_options)

    # Filter top runners based on selected year
    if selected_year != 'All':
        filtered_runners = top_runners[top_runners['Year'] == selected_year]
    else:
        filtered_runners = top_runners

    # Slider for minimum days run (applies to selected year filter)
    min_days = st.slider('Minimum Days Run', 
                         min_value=1, 
                         max_value=filtered_runners['Days Run'].max(), 
                         value=1)

    # Apply the slider filter
    filtered_runners = filtered_runners[filtered_runners['Days Run'] >= min_days]

    st.subheader(f'Top Runners ({selected_year}, Min {min_days} Days)')
    st.table(filtered_runners)

    # Search for specific runner and display their attendances
    selected_student = st.selectbox('Select a Student', df['Student Name'].unique())
    student_data = df[df['Student Name'] == selected_student]
    st.subheader(f'Attendance for {selected_student}')
    st.table(student_data)

# Room-level statistics: Number of unique runners per room
room_stats = (
    df.groupby('Room Number')['Student Name']
    .nunique()
    .reset_index()
    .rename(columns={'Student Name': 'Unique Runners'})
    .sort_values(by='Unique Runners', ascending=False)  # Sort by Unique Runners
    .reset_index(drop=True)  # Reset index for display
)

st.subheader('Runners by Room')
st.table(room_stats)
