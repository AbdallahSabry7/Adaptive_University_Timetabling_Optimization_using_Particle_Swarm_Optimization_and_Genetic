import Data
import models
import random
import logging
import heapq


def generate_Schedule():
    classNumb = 0
    schedule = []

    for dept in Data.departments:
        courses = dept.get_courses()
        for course in courses:
            newClass = models.Class(classNumb, dept, course)
            classNumb += 1

            newClass.set_meetingTime(random.choice(Data.Meeting_Times))
            newClass.set_room(random.choice(Data.Rooms))
            newClass.set_instructor(random.choice(course.get_instructors()))

            schedule.append(newClass)

    return schedule


import random

def generate_heuristic_schedule():
    class_id = 0
    schedule = []

    room_usage = {}         
    instructor_usage = {}   
    dept_time_usage = {}     

    
    courses = [(dept, course) for dept in Data.departments for course in dept.get_courses()]
    courses.sort(key=lambda x: -x[1].get_num_of_students())
    
    i = 0
    while i < len(courses):
        j = i + 1
        while j < len(courses) and courses[j][1].get_num_of_students() == courses[i][1].get_num_of_students():
            j += 1
        random.shuffle(courses[i:j])
        i = j

    for dept, course in courses:
        new_class = models.Class(class_id, dept, course)
        class_id += 1

        assigned = False

        meeting_times = random.sample(Data.Meeting_Times, len(Data.Meeting_Times))
        rooms = sorted(Data.Rooms, key=lambda r: r.get_seatingCapacity())
        random.shuffle(rooms)

        instructors = course.get_instructors()
        random.shuffle(instructors)

        for time in meeting_times:
            for room in rooms:
                if room.get_seatingCapacity() < course.get_num_of_students():
                    continue

                for instructor in instructors:
                    if (room, time) in room_usage:
                        continue
                    if (instructor, time) in instructor_usage:
                        continue
                    if (dept, time) in dept_time_usage:
                        continue


                    if random.random() < 0.2:
                        continue

                    new_class.set_meetingTime(time)
                    new_class.set_room(room)
                    new_class.set_instructor(instructor)

                    room_usage[(room, time)] = True
                    instructor_usage[(instructor, time)] = True
                    dept_time_usage[(dept, time)] = True

                    schedule.append(new_class)
                    assigned = True
                    break

                if assigned:
                    break
            if assigned:
                break


        if not assigned:
            new_class.set_meetingTime(random.choice(Data.Meeting_Times))
            new_class.set_room(random.choice(Data.Rooms))
            new_class.set_instructor(random.choice(instructors))
            schedule.append(new_class)

    return schedule



def generate_Schedule2():
    class_id = 0
    schedule = []

    for dept in Data.departments:
        courses = dept.get_courses()
        for course in courses:
            new_class = models.Class(class_id, dept, course)
            class_id += 1


            possible_rooms = [room for room in Data.Rooms 
                            if room.get_seatingCapacity() >= course.get_num_of_students()]
            chosen_room = random.choice(possible_rooms) if possible_rooms else random.choice(Data.Rooms)

            new_class.set_room(chosen_room)
            new_class.set_meetingTime(random.choice(Data.Meeting_Times))
            new_class.set_instructor(random.choice(course.get_instructors()))

            schedule.append(new_class)

    return schedule


def choose_weighted_room(course, meeting_time, room_usage):
    rooms = Data.Rooms
    weights = []

    for room in rooms:
        if room.get_seatingCapacity() < course.get_num_of_students():
            weights.append(0.1)
        else:
            usage_count = room_usage.get((room, meeting_time), 0)
            capacity_surplus = room.get_seatingCapacity() - course.get_num_of_students()
            weight = max(1.0 / (1 + usage_count), 0.1) * (1.0 / (1 + capacity_surplus))
            weights.append(weight)

    return random.choices(rooms, weights=weights, k=1)[0]

def choose_weighted_instructor(course, meeting_time, instructor_usage):
    instructors = course.get_instructors()
    weights = []

    for inst in instructors:
        usage_count = instructor_usage.get((inst, meeting_time), 0)
        weight = max(1.0 / (1 + usage_count), 0.1)
        weights.append(weight)

    return random.choices(instructors, weights=weights, k=1)[0]

def Weighted_generate_Schedule():
    class_id = 0
    schedule = []

    room_usage = {}
    instructor_usage = {}

    for dept in Data.departments:
        courses = dept.get_courses()
        for course in courses:
            new_class = models.Class(class_id, dept, course)
            class_id += 1

            meeting_time = random.choice(Data.Meeting_Times)

            room = choose_weighted_room(course, meeting_time, room_usage)
            instructor = choose_weighted_instructor(course, meeting_time, instructor_usage)

            new_class.set_meetingTime(meeting_time)
            new_class.set_room(room)
            new_class.set_instructor(instructor)

            room_usage[(room, meeting_time)] = room_usage.get((room, meeting_time), 0) + 1
            instructor_usage[(instructor, meeting_time)] = instructor_usage.get((instructor, meeting_time), 0) + 1

            schedule.append(new_class)

    return schedule


def fitness_function(position,base_schedule):
    penalties = 0

    schedule = decode_Schedule(base_schedule, position)  
    for i in range(len(schedule)):
        class1 = schedule[i]

        if class1.get_room().get_seatingCapacity() < class1.get_course().get_num_of_students():
            penalties += 5

        unused = class1.get_room().get_seatingCapacity() - class1.get_course().get_num_of_students()
        if unused > 15:
            penalties += 1

        for j in range(i + 1, len(schedule)):
            class2 = schedule[j]

            if class1.get_meetingTime() == class2.get_meetingTime():
                if class1.get_room() == class2.get_room():
                    penalties += 5

                if class1.get_instructor() == class2.get_instructor():
                    penalties += 5

                if class1.get_dept() == class2.get_dept():
                    penalties += 5

    return -penalties    


def encode_Schedule(schedule):
    encoded = []
    for cls in schedule:
        room_index = Data.Rooms.index(cls.get_room())
        meeting_time_index = Data.Meeting_Times.index(cls.get_meetingTime())
        instructor_index = cls.get_course().get_instructors().index(cls.get_instructor())

        encoded.extend([room_index, meeting_time_index, instructor_index])
    return encoded


def decode_Schedule(base_schedule, position):
    schedule = []
    for i in range(0, len(position), 3):
        base_class = base_schedule[i // 3]
        room_idx = Data.Rooms[position[i]]
        meeting_time_idx = Data.Meeting_Times[position[i + 1]]
        instructor_idx = base_class.get_course().get_instructors()[position[i + 2] % len(base_class.get_course().get_instructors())]

        new_class = models.Class(base_class.get_id(), base_class.get_dept(), base_class.get_course())
        new_class.set_instructor(instructor_idx)
        new_class.set_meetingTime(meeting_time_idx)
        new_class.set_room(room_idx)

        schedule.append(new_class)
    
    return schedule