import Data
import models
import random
import copy


class Particle:
    def __init__(self, generate_Schedule, encode_Schedule, decode_Schedule, fitness_function):
        self.schedule = generate_Schedule()
        self.base_schedule = copy.deepcopy(self.schedule)  
        self.position = encode_Schedule(self.schedule)
        self.velocity = [0] * len(self.position)
        self.fitness_function = fitness_function
        self.fitness = self.fitness_function(self.position,self.schedule)
        self.encode_Schedule = encode_Schedule
        self.decode_Schedule = decode_Schedule

        self.Personal_best_position = self.position.copy()
        self.Personal_best_fitness = self.fitness
    
    def __iter__(self):
        return self

    def update_personal_best(self):
        if self.fitness > self.Personal_best_fitness:
            self.Personal_best_fitness = self.fitness
            self.Personal_best_position = self.position.copy()

    def apply_velocity(self):
        new_position = []
        for i in range(len(self.position)):
            if i % 3 == 0:
                domain_size = len(Data.Rooms)
            elif i % 3 == 1:
                domain_size = len(Data.Meeting_Times)
            elif i % 3 == 2:
                class_index = i // 3
                domain_size = len(self.base_schedule[class_index].get_course().get_instructors())

            new_value = (self.position[i] + self.velocity[i]) % domain_size
            new_position.append(new_value)

        self.position = new_position
        self.schedule = self.decode_Schedule(self.base_schedule, self.position) 
        self.fitness = self.fitness_function(self.position,self.schedule)
        self.update_personal_best()

    def set_velocity(self, w, c1, c2, global_best_position):
        new_velocity = []
        for i in range(len(self.position)):
            r1 = random.random()
            r2 = random.random()

            inertia = w * self.velocity[i]
            cognitive = c1 * r1 * (self.Personal_best_position[i] - self.position[i])
            social = c2 * r2 * (global_best_position[i] - self.position[i])

            velocity = int(round(inertia + cognitive + social))
            velocity = max(-2, min(2, velocity))  

            new_velocity.append(velocity)

        self.velocity = new_velocity

    def update(self, new_position):
        self.position = new_position
        self.schedule = self.decode_Schedule(self.base_schedule, self.position)
        self.fitness = self.fitness_function(self.position, self.schedule)
        self.update_personal_best()

    def get_fitness(self):
        return self.fitness