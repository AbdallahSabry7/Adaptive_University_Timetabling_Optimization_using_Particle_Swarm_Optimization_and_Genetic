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
    
    def conflict_score(self,class_gene,all_classes):
        score = 0
        for other in all_classes:
            if other == class_gene:
                continue
            if class_gene.get_meetingTime() == other.get_meetingTime():
                if class_gene.get_room() == other.get_room():
                    score += 3
                if class_gene.get_instructor() == other.get_instructor():
                    score += 2
                if class_gene.get_dept() == other.get_dept():
                    score += 1
        if class_gene.get_course().get_num_of_students() > class_gene.get_room().get_seatingCapacity():
            score += 5

        return score
    
    def worst_gene_with_random_gene_mutation(self, chromosome, base_schedule, mr):
        if random.random() > mr:
            return chromosome

        decoded_chromosome = schedule.decode_Schedule(base_schedule, chromosome)

        worst_gene_index = max(
            range(len(decoded_chromosome)),
            key=lambda i: self.conflict_score(decoded_chromosome[i], decoded_chromosome)
        )

        start = worst_gene_index * 3
        end = start + 3

        random_schedule = schedule.generate_Schedule()
        random_encoded = schedule.encode_Schedule(random_schedule)

        new_chromosome = chromosome.copy()
        new_chromosome[start:end] = random_encoded[start:end] 
        return new_chromosome



