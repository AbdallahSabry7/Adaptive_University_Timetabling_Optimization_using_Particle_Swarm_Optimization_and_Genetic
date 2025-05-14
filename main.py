import Data
import models
import PSO
import scheduler_utils as scheduler
import Genetic
import random
# random.seed(42)
# random.seed(1)
random.seed(2)

def pso_main(max_iterations,particles_num,Mutaion_Type,crossover_Type,Selection_Type,w_start,c1,c2,w_end,mutation_rate,crossover_rate):
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
                match Mutaion_Type:
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

if __name__ == "__main__":
    best_schedule, best_fitness = pso_main()

    print(f"\n✅ Best Fitness Achieved: {best_fitness}")
    print("📅 Final Timetable:")
    for cls in best_schedule:
        print(f"Class ID {cls.get_id()} | Dept: {cls.get_dept().get_name()} | "
            f"Course: {cls.get_course().get_name()} | Room: {cls.get_room().get_number()} | "
            f"Time: {cls.get_meetingTime().get_time()} | Instructor: {cls.get_instructor().get_name()}")