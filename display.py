import pandas as pd

# Data for Year 1
data_year_1 = {
    'Year': ['Year 1'] * 8,
    'Day': ['Sunday', 'Sunday', 'Monday', 'Sunday', 'Monday', 'Sunday', 'Sunday', 'Sunday'],
    'Timeslot': ['14:00 - 14:45', '08:30 - 09:15', '10:30 - 11:15', '15:30 - 16:15', '15:30 - 16:15', '10:30 - 11:15', '09:15 - 10:00', '14:45 - 15:30'],
    'Slot': ['5', '1', '10', '7', '14', '3', '2', '6'],
    'Course': ['Math', 'Math', 'Math', 'Math', 'Physics', 'Physics', 'Chemistry', 'Chemistry'],
    'TeacherID': ['3', '3', '3', '1', '1', '1', '2', '2'],
    'ClassID': ['103', '102', '101', '103', '102', '101', '103', '103']
}

# Data for Year 2
data_year_2 = {
    'Year': ['Year 2'] * 8,
    'Day': ['Sunday', 'Monday', 'Monday', 'Sunday', 'Monday', 'Sunday', 'Monday', 'Monday'],
    'Timeslot': ['14:00 - 14:45', '10:30 - 11:15', '14:00 - 14:45', '11:15 - 12:00', '14:45 - 15:30', '09:15 - 10:00', '08:30 - 09:15', '11:15 - 12:00'],
    'Slot': ['5', '10', '12', '4', '13', '2', '8', '11'],
    'Course': ['Math', 'Math', 'Math', 'Math', 'Biology', 'Biology', 'Chemistry', 'Chemistry'],
    'TeacherID': ['1', '1', '3', '3', '3', '3', '2', '2'],
    'ClassID': ['102', '103', '102', '103', '101', '101', '102', '102']
}

# Combine Year 1 and Year 2 data
data_combined = pd.concat([pd.DataFrame(data_year_1), pd.DataFrame(data_year_2)])

# Display the combined timetable sorted by Year, Day, and Slot
df_sorted_combined = data_combined.sort_values(by=['Year', 'Day', 'Slot'])

# Display the organized timetable
print("Organized Timetable (Year 1 and Year 2):")
print(df_sorted_combined.to_string(index=False))
