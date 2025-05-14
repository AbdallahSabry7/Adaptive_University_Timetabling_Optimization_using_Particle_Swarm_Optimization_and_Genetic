import Data
import models
import PSO
import scheduler_utils as scheduler
import Genetic
import random
import copy
# random.seed(42)
# random.seed(1)
random.seed(2)

def pso_main(max_iterations, particles_num, w_start, c1, c2, w_end):
    swarm = [
        PSO.Particle(
            scheduler.generate_Schedule,
            scheduler.encode_Schedule,
            scheduler.decode_Schedule,
            scheduler.fitness_function
        )
        for _ in range(particles_num)
    ]

    global_best_particle = max(swarm, key=lambda p: p.fitness)
    global_best_position = global_best_particle.position.copy()
    global_best_fitness = global_best_particle.fitness

    iteration = 0
    global_fitness_overtime = []
    while global_best_fitness != 0 and iteration <= max_iterations:
        w = w_start - (w_start - w_end) * (iteration / max_iterations)
        print(f"Iteration {iteration + 1} - Best Fitness: {global_best_fitness}")

        for particle in swarm:
            particle.set_velocity(w, c1, c2, global_best_position)
            particle.apply_velocity()

            if particle.fitness > global_best_fitness:
                global_best_fitness = particle.fitness
                global_best_position = particle.position.copy()
                global_best_particle = particle

        iteration = iteration + 1
        global_fitness_overtime.append(global_best_fitness)

    best_schedule = scheduler.decode_Schedule(global_best_particle.base_schedule, global_best_position)
    return best_schedule, global_best_fitness, global_fitness_overtime



def hybrid_main(max_iterations, particles_num, Mutation_Type, crossover_Type, Selection_Type, w_start, c1, c2, w_end, mutation_rate, crossover_rate):
    swarm = [
        PSO.Particle(
            scheduler.generate_Schedule,
            scheduler.encode_Schedule,
            scheduler.decode_Schedule,
            scheduler.fitness_function
        )
        for _ in range(particles_num)
    ]

    global_best_particle = max(swarm, key=lambda p: p.fitness)
    global_best_position = global_best_particle.position.copy()
    global_best_fitness = global_best_particle.fitness

    genetic = Genetic.Genetic(mutation_rate,crossover_rate)
    iteration = 0
    global_fitness_overtime=[]
    while global_best_fitness != 0 and iteration <= max_iterations:
        w = w_start - (w_start - w_end) * (iteration / max_iterations)
        print(f"Iteration {iteration + 1} - Best Fitness: {global_best_fitness}")
        if (iteration+1) % 10 == 0:
                print(f"Rates — NCR: {ncr:.3f}, NMR: {nmr:.3f}")

        top_particles = sorted(swarm, key=lambda p: p.fitness, reverse=True)[:int(0.1 * particles_num)]

        for particle in swarm:
            others = [p for p in swarm if p is not particle]
            particle.set_velocity(w, c1, c2, global_best_position)
            particle.apply_velocity()
            ncr,nmr = genetic.update_rates(iteration,max_iterations)
            if ncr > random.random():
                match Selection_Type:
                    case "Ranked":
                        other_particle = genetic.ranked_selection(others)
                    case "Tournament":
                        other_particle = genetic.tournament_selection(others)
                match crossover_Type:
                    case "Single Point":
                        new_particle = genetic.one_point_crossover(particle.position, other_particle)
                    case "Two Point":
                        new_particle = genetic.two_point_crossover(particle.position, other_particle)
                    case "Uniform":
                        new_particle = genetic.uniform_crossover(particle.position, other_particle)
                    case "sector_based":
                        new_particle = genetic.sector_based_crossover(particle.position, other_particle)
                    case "Conflict Aware":
                        new_particle = genetic.conflict_aware_crossover(particle.position, other_particle, base_schedule=particle.base_schedule)
                particle.update(new_particle)
            
            if nmr > random.random():
                match Mutation_Type:
                    case "WGWRGM":
                        new_particle = genetic.worst_gene_with_random_gene_mutation(particle.position,particle.base_schedule)
                    case "random_reinitialization_M":
                        new_particle = genetic.random_reinitialization_mutation(particle.position, nmr)   
                    case "swap_class_assignments_M":
                        new_particle = genetic.swap_class_assignments_mutation(particle.position)
                    case "field_mutation":
                        new_particle = genetic.field_mutation(particle.position)
                particle.update(new_particle)

            if particle.fitness > global_best_fitness:
                global_best_fitness = particle.fitness
                global_best_position = particle.position.copy()
                global_best_particle = particle

        worst_particles = sorted(swarm, key=lambda p: p.fitness)[:int(0.1 * particles_num)]
        for worst, best in zip(worst_particles, top_particles):
            worst.update(best.position)

        iteration = iteration + 1
        global_fitness_overtime.append(global_best_fitness)

    best_schedule = scheduler.decode_Schedule(global_best_particle.base_schedule, global_best_position)
    return best_schedule, global_best_fitness,global_fitness_overtime


def genetic_main(max_iterations, population_size, Mutation_Type, crossover_Type, Selection_Type, mutation_rate, crossover_rate, survival_type):
    genetic = Genetic.Genetic(mutation_rate, crossover_rate)
    base_schedule = scheduler.generate_Schedule()
    population = genetic.generate_population(base_schedule, population_size)

    best_schedule = None
    best_fitness = float('-inf')
    global_fitness_overtime = []
    iteration = 0

    while iteration < max_iterations and best_fitness != 0:
        
        ncr, nmr = genetic.update_rates(iteration, max_iterations)
        iteration = iteration + 1
        

        for individual in population:
            fitness = scheduler.fitness_function(individual.position, base_schedule)
            if fitness > best_fitness:
                best_fitness = fitness
                best_schedule = individual

        new_population = []
        for individual in population:
            others = [p for p in population if p is not individual]
            if ncr > random.random():
                match Selection_Type:
                    case "Ranked":
                        selected = genetic.ranked_selection(others)
                    case "Tournament":
                        selected = genetic.tournament_selection(others)
                match crossover_Type:
                    case "Single Point":
                        new_particle = genetic.one_point_crossover(individual.position, selected)
                    case "Two Point":
                        new_particle = genetic.two_point_crossover(individual.position, selected)
                    case "Uniform":
                        new_particle = genetic.uniform_crossover(individual.position, selected)
                    case "sector_based":
                        new_particle = genetic.sector_based_crossover(individual.position, selected)
                    case "Conflict Aware":
                        new_particle = genetic.conflict_aware_crossover(individual.position, selected, base_schedule=individual.base_schedule)
                        individual.update(new_particle)
                new_population.append(individual)

        for individual in new_population:
            if nmr > random.random():
                match Mutation_Type:
                    case "WGWRGM":
                        new_particle = genetic.worst_gene_with_random_gene_mutation(individual.position, individual.base_schedule)
                    case "random_reinitialization_M":
                        new_particle = genetic.random_reinitialization_mutation(individual.position, nmr)
                    case "swap_class_assignments_M":
                        new_particle = genetic.swap_class_assignments_mutation(individual.position)
                    case "field_mutation":
                        new_particle = genetic.field_mutation(individual.position)
                individual.update(new_particle)

        combined = population + new_population
        if survival_type == "elitism":
            elite_count = max(1, int(0.1 * population_size))
            elite_individuals = sorted(population, key=lambda x: x.fitness, reverse=True)[:elite_count]
            worst_individuals_indices = sorted(range(len(new_population)), key=lambda i: new_population[i].fitness)[:elite_count]
            for idx, elite in zip(worst_individuals_indices, elite_individuals):
                new_population[idx] = copy.deepcopy(elite)
        elif survival_type == "tournament":
            tournament_size = 3
            survivors = []
            for _ in range(population_size):
                selected = random.sample(combined, tournament_size)
                winner = max(selected, key=lambda x: x.fitness)
                survivors.append(copy.deepcopy(winner))
            new_population = survivors
        elif survival_type == "ranked":
            sorted_population = sorted(combined, key=lambda x: x.fitness, reverse=True)
            probabilities = [1 / (i + 1) for i in range(len(sorted_population))]
            total = sum(probabilities)
            probabilities = [p / total for p in probabilities]
            new_population = random.choices(sorted_population, weights=probabilities, k=population_size)
        elif survival_type == "generational":
            new_population = sorted(new_population, key=lambda x: x.fitness, reverse=True)[:population_size]
                


        population = new_population
        print(f"Iteration {iteration + 1} - Best Fitness: {best_fitness}")
        global_fitness_overtime.append(best_fitness)

    best_schedule = scheduler.decode_Schedule(best_schedule.base_schedule, best_schedule.position)
    return best_schedule, best_fitness, global_fitness_overtime


if __name__ == "__main__":
    best_schedule, best_fitness, global_fitness_overtime = genetic_main(
        max_iterations=100,
        population_size=50,
        Mutation_Type="WGWRGM",
        crossover_Type="Single Point",
        Selection_Type="Tournament",
        mutation_rate=0.3,
        crossover_rate=0.8
    )

    print(f"\n✅ Best Fitness Achieved: {best_fitness}")
    print("📅 Final Timetable:")
    for cls in best_schedule:
        print(f"Class ID {cls.get_id()} | Dept: {cls.get_dept().get_name()} | "
            f"Course: {cls.get_course().get_name()} | Room: {cls.get_room().get_number()} | "
            f"Time: {cls.get_meetingTime().get_time()} | Instructor: {cls.get_instructor().get_name()}")