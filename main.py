import Data
import models
import PSO
import scheduler_utils as scheduler
import Genetic
import random
random.seed(42)
def pso_main(particles_num=30, max_iterations=1000, w_start=0.9,w_end=0.4, c1=1, c2=2):
    x = int(input("select 1 or 2 or 3 or 4 for mutation type: \n1. Worst Gene with Random Gene Mutation\n2. Random Reinitialization Mutation\n3. Swap Class Assignments Mutation\n4. Field Mutation\n"))
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

    genetic = Genetic.Genetic()
    iteration = 0
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
                other_particle = genetic.tournament_selection(others)
                new_particle =genetic.crossover(particle.position,other_particle)
                particle.update(new_particle)
            
            if nmr > random.random():
                match x:
                    case 1:
                        new_particle = genetic.worst_gene_with_random_gene_mutation(particle.position,particle.base_schedule)
                    case 2:
                        new_particle = genetic.random_reinitialization_mutaion(particle.position, nmr)   
                    case 3:
                        new_particle = genetic.swap_class_assignments_mutation(particle.position)
                    case 4:
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
    best_schedule = scheduler.decode_Schedule(global_best_particle.base_schedule, global_best_position)
    return best_schedule, global_best_fitness

if __name__ == "__main__":
    best_schedule, best_fitness = pso_main()

    print(f"\n✅ Best Fitness Achieved: {best_fitness}")
    print("📅 Final Timetable:")
    for cls in best_schedule:
        print(f"Class ID {cls.get_id()} | Dept: {cls.get_dept().get_name()} | "
            f"Course: {cls.get_course().get_name()} | Room: {cls.get_room().get_number()} | "
            f"Time: {cls.get_meetingTime().get_time()} | Instructor: {cls.get_instructor().get_name()}")