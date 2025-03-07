import pandas as pd
import streamlit as st

# Load data
url = 'https://docs.google.com/spreadsheets/d/1pOxce5luIYRygXP90dh01-HdXaW2-9i4wkGyK3ycYIo/export?format=csv&gid=20815831'
df = pd.read_csv(url)

# Data cleaning and formatting
df['Student Name'] = df['Student Name'].str.lower().str.strip()
df['Timestamp'] = pd.to_datetime(df['Timestamp'], dayfirst=True)
df['Date'] = pd.to_datetime(df['Timestamp'].dt.date)
df['Room Number'] = df['Room Number'].str.lower().str.strip().str.replace(r'\broom\b\s*', '', regex=True)
df['Room Number'] = df['Room Number'].str.replace('kindy c', 'kindy')
df = df.drop(labels=['Laps Completed (Sprints / Laps)', 'Timestamp'], axis=1)
df = df.sort_values(by='Date')

# Main layout for filters
st.title('Carnaby Running Club Stats')

# Move filters to the main page
view = st.selectbox('View Stats By', ['Student Name', 'Date'], key='view_selector')

st.markdown("<hr style='border-top: 2px solid #082251; margin: 20px 0;'>", unsafe_allow_html=True)

if view == 'Date':
    # Title
    st.header('Run Data By Date')
    st.markdown("<hr style='border-top: 2px solid #082251; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Date-specific filter
    st.subheader('Attendance by Date')
    date_options = df['Date'].dt.strftime('%d-%m-%Y').unique()
    selected_date = st.selectbox('Select a Date', date_options, key='date_filter')

    # Filter data based on selected date
    filtered_data = df[df['Date'].dt.strftime('%d-%m-%Y') == selected_date]
    filtered_data['Date'] = filtered_data['Date'].dt.strftime('%d-%m-%Y')

    # Display total runs per day
    runs_per_day = df.groupby('Date')['Student Name'].count().reset_index()
    runs_per_day.columns = ['Date', 'Total Runs']
    runs_per_day['Date'] = runs_per_day['Date'].dt.strftime('%d-%m-%Y')
    
    st.subheader('Total Runs by Date')
    st.dataframe(runs_per_day, hide_index=True, use_container_width=True)
    st.subheader('Total Runs Trend')

    # Ensure 'Date' is a datetime object and sort chronologically
    runs_per_day['Date'] = pd.to_datetime(runs_per_day['Date'], dayfirst=True)
    runs_per_day = runs_per_day.sort_values(by='Date')
    
    # Format 'Date' as 'm-d-y' for display on the x-axis
    runs_per_day['Date_Display'] = runs_per_day['Date'].dt.strftime('%Y-%m-%d')
    
    # Set 'Date_Display' as the index for correct display order
    runs_per_day.set_index('Date_Display', inplace=True)
        
    
    # Plot the line chart with m-d-y formatted dates on the x-axis
    st.line_chart(runs_per_day['Total Runs'], use_container_width=True)
    
    # Total unique runners
    unique_count = len(df['Student Name'].unique())
    st.subheader('Total Unique Runners')
    st.write(f'Number of unique students: {unique_count}')

    # Room-level statistics
    room_stats = (
        filtered_data.groupby(['Year','Room Number'])['Student Name']
        .nunique()
        .reset_index()
        .rename(columns={'Student Name': 'Unique Runners'})
        .sort_values(by='Unique Runners', ascending=False)
        .reset_index(drop=True)
    )
    
    st.subheader('Runners by Year and Room For Seleced Date')
    st.dataframe(room_stats, hide_index=True, use_container_width=True)
    
    # Runner List By Date and Room
    st.subheader(f'Runners on {selected_date} for Selected Room')
    # add year and room number filter
    rooms = df['Room Number'].sort_values().unique()
    selected_rooms = st.selectbox('Select a Room', rooms, key='room_filter')
    
    filtered_data = df[df['Date'].dt.strftime('%d-%m-%Y') == selected_date]
    rooms_filtered_data = filtered_data.copy()
    rooms_filtered_data['Date'] = rooms_filtered_data['Date'].dt.strftime('%d-%m-%Y')
    rooms_filtered_data = rooms_filtered_data[rooms_filtered_data['Room Number']==selected_rooms]
        
    st.dataframe(rooms_filtered_data, hide_index=True, use_container_width=True)

elif view == 'Student Name':
    
    # Title
    st.header('Run Data By Student')
    
    st.markdown("<hr style='border-top: 2px solid #082251; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Year and days run filters
    year_options = ['All'] + df['Year'].sort_values().unique().tolist()
    selected_year = st.selectbox('Select School Year', year_options, key='year_filter')
    
    top_runners = (
        df.groupby(['Student Name', 'Year', 'Room Number'])
        .size()
        .reset_index(name='Days Run')
        .sort_values(by='Days Run', ascending=False)
    )

    filtered_runners = top_runners if selected_year == 'All' else top_runners[top_runners['Year'] == selected_year]
    min_days = st.slider('Minimum Days Run', min_value=1, max_value=filtered_runners['Days Run'].max(), value=1, key='min_days_filter')
    filtered_runners = filtered_runners[filtered_runners['Days Run'] >= min_days]

    st.subheader(f'Top Runners ({selected_year}, Min {min_days} Days)')
    st.table(filtered_runners)
    
    # Total unique runners
    unique_count_filtered = len(filtered_runners['Student Name'].unique())
    st.subheader(f'Numnber of Unique Runners ({selected_year}, Min {min_days} Days)')
    st.write(f'Number of unique students: {unique_count_filtered}')

    # Runner-specific attendance
    selected_student = st.selectbox('Select a Student', df['Student Name'].unique(), key='student_filter')
    student_data = df[df['Student Name'] == selected_student]
    student_data['Date'] = student_data['Date'].dt.strftime('%d-%m-%Y')

    st.subheader(f'Attendance for {selected_student}')
    st.table(student_data)
