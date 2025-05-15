import Data
import models
import PSO
import scheduler_utils as scheduler
from Genetic import Genetic
import random
import copy
random.seed(42)
# random.seed(1)
# random.seed(2)

def pso_main(max_iterations, particles_num, w_start, c1, c2, w_end, log_callback=None):
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
        log_callback(f"Iteration {iteration + 1} - Best Fitness: {global_best_fitness}")

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



def hybrid_main(max_iterations, particles_num, Mutation_Type, crossover_Type, Selection_Type, w_start, c1, c2, w_end,
                mutation_rate, crossover_rate, initialization_type="random", log_callback=None):
    if initialization_type == "random":
        swarm = [
            PSO.Particle(
                scheduler.generate_Schedule,
                scheduler.encode_Schedule,
                scheduler.decode_Schedule,
                scheduler.fitness_function
            )
            for _ in range(particles_num)
        ]
    elif initialization_type == "heuristic":
        swarm = [
            PSO.Particle(
                scheduler.generate_heuristic_schedule,
                scheduler.encode_Schedule,
                scheduler.decode_Schedule,
                scheduler.fitness_function
            )
            for _ in range(particles_num)
        ]
    elif initialization_type == "weighted":
        swarm = [
            PSO.Particle(
                scheduler.Weighted_generate_Schedule,
                scheduler.encode_Schedule,
                scheduler.decode_Schedule,
                scheduler.fitness_function
            )
            for _ in range(particles_num)
        ]

    global_best_particle = max(swarm, key=lambda p: p.fitness)
    global_best_position = global_best_particle.position.copy()
    global_best_fitness = global_best_particle.fitness

    genetic = Genetic(mutation_rate,crossover_rate)
    iteration = 0
    global_fitness_overtime=[]
    while global_best_fitness != 0 and iteration <= max_iterations:
        w = w_start - (w_start - w_end) * (iteration / max_iterations)
        log_callback(f"Iteration {iteration + 1} - Best Fitness: {global_best_fitness}")
        if (iteration+1) % 10 == 0:
                log_callback(f"Rates — NCR: {ncr:.3f}, NMR: {nmr:.3f}")

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

def genetic_main(max_generations, population_size, Mutation_Type, crossover_Type, Selection_Type,
                mutation_rate, crossover_rate, initialization_type ="random",Survival_Type="elitism", log_callback=None):


    base_schedule = scheduler.generate_Schedule()

    genetic = Genetic(mutation_rate, crossover_rate)
    population = genetic.generate_population(base_schedule, population_size, initialization_type=initialization_type)

    best_individual = max(population, key=lambda p: p.fitness)
    best_fitness = best_individual.fitness
    best_position = best_individual.position.copy()

    fitness_over_time = []

    for generation in range(max_generations):
        ncr, nmr = genetic.update_rates(generation, max_generations)

        log_callback(f"Generation {generation + 1} - Best Fitness: {best_fitness:.3f}")
        if (generation + 1) % 10 == 0:
            log_callback(f"Rates — NCR: {ncr:.3f}, NMR: {nmr:.3f}")

        # Survival Selection
        if Survival_Type == "elitism":
            elite_count = 2
            elites = sorted(population, key=lambda p: p.fitness, reverse=True)[:elite_count]
            new_population = elites[:]  # start with elite survivors
        if Survival_Type == "generational":
            new_population = []


        while len(new_population) < population_size:
            # Selection
            match Selection_Type:
                case "Ranked":
                    parent1 = genetic.ranked_selection(population)
                    parent2 = genetic.ranked_selection(population)
                case "Tournament":
                    parent1 = genetic.tournament_selection(population)
                    parent2 = genetic.tournament_selection(population)

            # Crossover
            if ncr > random.random():
                match crossover_Type:
                    case "Single Point":
                        child_position = genetic.one_point_crossover(parent1, parent2)
                    case "Two Point":
                        child_position = genetic.two_point_crossover(parent1, parent2)
                    case "Uniform":
                        child_position = genetic.uniform_crossover(parent1, parent2)
                    case "sector_based":
                        child_position = genetic.sector_based_crossover(parent1, parent2)
                    case "Conflict Aware":
                        child_position = genetic.conflict_aware_crossover(parent1, parent2, base_schedule)
                    case _:
                        child_position = parent1.copy()
            else:
                child_position = parent1.copy()

            # Mutation
            if nmr > random.random():
                match Mutation_Type:
                    case "WGWRGM":
                        child_position = genetic.worst_gene_with_random_gene_mutation(child_position, base_schedule)
                    case "random_reinitialization_M":
                        child_position = genetic.random_reinitialization_mutation(child_position, nmr)
                    case "swap_class_assignments_M":
                        child_position = genetic.swap_class_assignments_mutation(child_position)
                    case "field_mutation":
                        child_position = genetic.field_mutation(child_position)

            # Fitness evaluation
            child = PSO.Particle(
                lambda: scheduler.generate_Schedule(),
                scheduler.encode_Schedule,
                scheduler.decode_Schedule,
                scheduler.fitness_function
            )
            child.position = child_position
            child.fitness = scheduler.fitness_function(child_position, base_schedule)
            new_population.append(child)

        population = new_population

        current_best = max(population, key=lambda p: p.fitness)
        if current_best.fitness > best_fitness:
            best_fitness = current_best.fitness
            best_position = current_best.position.copy()
            best_individual = current_best

        fitness_over_time.append(best_fitness)

        if best_fitness == 0:
            break

    best_schedule = scheduler.decode_Schedule(base_schedule, best_position)
    return best_schedule, best_fitness, fitness_over_time


