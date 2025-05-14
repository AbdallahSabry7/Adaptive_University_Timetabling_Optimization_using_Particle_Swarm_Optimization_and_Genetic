import models


# Room data(room name, seating capacity)
Rooms = [
    models.Room('R1', 25),
    models.Room('R2', 30),
    models.Room('R3', 35),
    models.Room('R4', 40),
    models.Room('R5', 45),
    models.Room('R6', 50),
    models.Room('R7', 55),
    models.Room('R8', 60),
    models.Room('R9', 65),
    models.Room('R10', 70)
]

# Meeting times data(id, time slot)
Meeting_Times = [
    models.Meeting_Time('MT1', 'Sunday 08:00 - 09:30'),
    models.Meeting_Time('MT2', 'Sunday 09:30 - 11:00'),
    models.Meeting_Time('MT3', 'Sunday 11:00 - 12:30'),
    models.Meeting_Time('MT4', 'Monday 08:00 - 09:30'),
    models.Meeting_Time('MT5', 'Monday 09:30 - 11:00'),
    models.Meeting_Time('MT6', 'Monday 11:00 - 12:30'),
    models.Meeting_Time('MT7', 'Tuesday 08:00 - 09:30'),
    models.Meeting_Time('MT8', 'Tuesday 09:30 - 11:00'),
    models.Meeting_Time('MT9', 'Tuesday 11:00 - 12:30'),
    models.Meeting_Time('MT10', 'Wednesday 08:00 - 09:30'),
    models.Meeting_Time('MT11', 'Wednesday 09:30 - 11:00'),
    models.Meeting_Time('MT12', 'Wednesday 11:00 - 12:30'),
    models.Meeting_Time('MT13', 'Thursday 08:00 - 09:30'),
    models.Meeting_Time('MT14', 'Thursday 09:30 - 11:00'),
    models.Meeting_Time('MT15', 'Thursday 11:00 - 12:30')
]

# Instructors data(id, name)
instructors = [
    models.Instructor('I1', 'ABDALLAH'),
    models.Instructor('I2', 'Sara'),
    models.Instructor('I3', 'Ahmed'),
    models.Instructor('I4', 'Mohamed'),
    models.Instructor('I5', 'Zahra'),
    models.Instructor('I6', 'Omar'),
    models.Instructor('I7', 'Laila'),
    models.Instructor('I8', 'Khaled'),
    models.Instructor('I9', 'Yasmin'),
    models.Instructor('I10', 'Ali'),
    models.Instructor('I11', 'Nour'),
    models.Instructor('I12', 'Salma'),
    models.Instructor('I13', 'Hassan'),
    models.Instructor('I14', 'Rania'),
    models.Instructor('I15', 'Tamer')
]

# Courses data(course id, course name, number of students, list of instructors)
Courses = [
    models.Course('C1', 'Math', 30, [instructors[0], instructors[1]]),
    models.Course('C2', 'Physics', 40, [instructors[2], instructors[3]]),
    models.Course('C3', 'Data Structures', 35, [instructors[4], instructors[5]]),
    models.Course('C4', 'Machine Learning', 45, [instructors[6], instructors[7]]),
    models.Course('C5', 'NLP', 30, [instructors[8], instructors[9]]),
    models.Course('C6', 'Databases', 50, [instructors[10], instructors[11]]),
    models.Course('C7', 'Logic Design', 25, [instructors[0], instructors[12]]),
    models.Course('C8', 'Operating Systems', 40, [instructors[1], instructors[13]]),
    models.Course('C9', 'Computer Networks', 35, [instructors[2], instructors[14]]),
    models.Course('C10', 'AI Ethics', 30, [instructors[3], instructors[5]]),
    models.Course('C11', 'Web Development', 50, [instructors[4], instructors[10]]),
    models.Course('C12', 'Cybersecurity', 45, [instructors[6], instructors[11]]),
    models.Course('C13', 'Software Testing', 40, [instructors[7], instructors[12]]),
    models.Course('C14', 'Distributed Systems', 35, [instructors[8], instructors[13]]),
    models.Course('C15', 'Compilers', 30, [instructors[9], instructors[14]]),
    models.Course('C16', 'Computer Graphics', 25, [instructors[0], instructors[4]]),
    models.Course('C17', 'Information Security', 50, [instructors[1], instructors[6]]),
    models.Course('C18', 'Big Data', 55, [instructors[2], instructors[5]]),
    models.Course('C19', 'Cloud Computing', 60, [instructors[3], instructors[10]]),
    models.Course('C20', 'Reinforcement Learning', 45, [instructors[7], instructors[8]])
]

# Departments data(department name, list of courses)
departments = [
    models.Department('CS', [Courses[0], Courses[1], Courses[6], Courses[10]]),
    models.Department('AI', [Courses[2], Courses[3], Courses[4], Courses[18]]),
    models.Department('IS', [Courses[5], Courses[7], Courses[15]]),
    models.Department('SE', [Courses[8], Courses[11], Courses[16]]),
    models.Department('CE', [Courses[9], Courses[12], Courses[13], Courses[17]]),
    models.Department('DS', [Courses[14], Courses[19]])
]
