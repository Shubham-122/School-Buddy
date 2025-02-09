import pandas as pd
import numpy as np

# Load data for all years and schools
years = [2019, 2020, 2021]
schools = ['Vidya Mandir', 'St. Joseph', 'DPS', 'Birla HS', 'International']

# Create combined dataframe
all_data = pd.DataFrame()

for year in years:
    file_path = f'Bangalore Schools {year}.xlsx'
    for school in schools:
        df = pd.read_excel(file_path, sheet_name=school)
        df['Year'] = year
        df['School'] = school
        all_data = pd.concat([all_data, df], ignore_index=True)

# Clean column names
all_data.columns = all_data.columns.str.strip()

# Problem 1: Top performer per school (cumulative marks 2019-21)
total_marks = all_data.groupby(['School', 'Student Roll', 'Student Name']).sum(numeric_only=True)
total_marks['Total'] = total_marks.sum(axis=1)
solution_1 = total_marks.groupby('School').apply(lambda x: x.nlargest(1, 'Total')).reset_index()
solution_1 = solution_1[['School', 'Student Roll', 'Student Name', 'Total']]

# Problem 2: Rank 10 comparison for 2020
year_2020 = all_data[all_data['Year'] == 2020]
year_2020['Total'] = year_2020.iloc[:, 2:-2].sum(axis=1)
year_2020['Rank'] = year_2020.groupby('School')['Total'].rank(ascending=False, method='min')
rank_10 = year_2020[year_2020['Rank'] == 10].sort_values('Total', ascending=False)
solution_2 = rank_10[['School', 'Student Name', 'Total']]

# Problem 3: Highest improvement per subject 2019-2021
pivot_data = all_data.pivot_table(index=['Student Roll', 'Student Name', 'School'], 
                                columns='Year', 
                                values=[c for c in all_data.columns if c not in ['Student Roll', 'Student Name', 'School', 'Year']])
improvements = {}
for subject in pivot_data.columns.levels[0]:
    if subject in ['Student Roll', 'Student Name', 'School']: continue
    improvements[subject] = (pivot_data[subject][2021] - pivot_data[subject][2019]).idxmax()
solution_3 = pd.DataFrame.from_dict(improvements, orient='index').reset_index()
solution_3.columns = ['Subject', 'Student Roll', 'Student Name', 'School']

# Problem 4: Best school for each stream
streams = {
    'Arts': ['Hindi', 'English', 'History', 'Geography', 'Civics'],
    'Science': ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science'],
    'Commerce': ['Hindi', 'English', 'Mathematics', 'Computer Science', 'Physical Education']
}

stream_scores = {}
for stream, subjects in streams.items():
    stream_df = all_data.groupby('School')[subjects].mean().mean(axis=1)
    stream_scores[stream] = stream_df.idxmax()
solution_4 = pd.DataFrame(stream_scores.items(), columns=['Stream', 'Best School'])

# Problem 5: Category counts per school
categories = [
    (0, 20, 'Very Poor'),
    (20, 40, 'Poor'), 
    (40, 60, 'Average'),
    (60, 80, 'Good'),
    (80, 100, 'Very Good')
]

category_data = []
for (school, year), group in all_data.groupby(['School', 'Year']):
    avg_marks = group.iloc[:, 2:-2].mean(axis=1)
    counts = {}
    for low, high, cat in categories:
        counts[cat] = avg_marks.between(low if low !=0 else -np.inf, high).sum()
    counts['School'] = school
    counts['Year'] = year
    category_data.append(counts)
    
solution_5 = pd.DataFrame(category_data)

# Problem 6: Best school per year based on Good+Very Good
good_cats = ['Good', 'Very Good']
solution_6 = solution_5.groupby(['Year', 'School']).apply(
    lambda x: x[good_cats].sum(axis=1)).reset_index()
solution_6.columns = ['Year', 'School', 'Good+']
solution_6 = solution_6.loc[solution_6.groupby('Year')['Good+'].idxmax()]

# Problem 7: Fastest-growing school
growth = all_data.groupby(['School', 'Year']).mean(numeric_only=True).mean(axis=1).unstack()
growth['Overall Growth'] = growth[2021] - growth[2019]

stream_growth = {}
for stream, subjects in streams.items():
    stream_growth[stream] = all_data.groupby(['School', 'Year'])[subjects].mean().mean(axis=1).unstack()
    stream_growth[stream]['Growth'] = stream_growth[stream][2021] - stream_growth[stream][2019]
    
solution_7_overall = growth['Overall Growth'].nlargest(1).reset_index()
solution_7_stream = pd.DataFrame({stream: df['Growth'].nlargest(1) for stream, df in stream_growth.items()})

# Save all solutions
solutions = {
    'solution_1': solution_1,
    'solution_2': solution_2,
    'solution_3': solution_3,
    'solution_4': solution_4,
    'solution_5': solution_5,
    'solution_6': solution_6,
    'solution_7_overall': solution_7_overall,
    'solution_7_stream': solution_7_stream
}

for name, df in solutions.items():
    df.to_csv(f'{name}.csv', index=False)
