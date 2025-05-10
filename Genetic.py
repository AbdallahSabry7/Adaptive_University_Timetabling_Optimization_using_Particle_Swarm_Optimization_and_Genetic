import random
import scheduler_utils as schedule
import PSO
class Genetic:
    def __init__(self,cr=0.9, mr=0.3):
        self.cr = cr
        self.mr = mr
    
    def __iter__(self):
        pass

    def crossover(self, chromosome1, chromosome2):
        new_chromosome = []
        for i in range(len(chromosome1)):
            if random.random() < 0.5:
                new_chromosome.append(chromosome1[i])
            else:
                new_chromosome.append(chromosome2[i])
        return new_chromosome

    
    def mutation(self, chromosome, mr):
        new_values = schedule.encode_Schedule(schedule.generate_Schedule())
        for i in range(len(chromosome)):
            if mr > random.random():
                chromosome[i] = new_values[i]
        return chromosome

    def ranked_selection(self,population,selection_pressure=1.5, maximize=True):
        sorted_pop = sorted(population,key=lambda p: p.get_fitness(),reverse=maximize)
        ranks = range(1,len(sorted_pop)+1)
        probabilities = [
            (2 - selection_pressure) + 2 * (selection_pressure - 1) * (len(sorted_pop) - r) / (len(sorted_pop) - 1)
            for r in ranks
        ]   
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
        particle =random.choices(sorted_pop, weights=probabilities, k=1)[0]
        return particle.position

    def tournament_selection(self, population, k=3):
        selected = random.sample(population, k)
        return max(selected, key=lambda p: p.get_fitness()).position

    def update_rates(self,t, t_max):
        ncr = self.cr * (t / t_max)
        nmr = self.mr * ((t_max - t) / t_max)
        return ncr, nmr
    