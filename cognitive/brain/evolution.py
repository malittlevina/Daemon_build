import random
import copy

class EvolutionaryPlanner:
    """
    Generates action plans by simulating evolution (Mutation/Selection)
    rather than asking an LLM.
    """
    def __init__(self, action_space):
        self.action_space = action_space # List of possible actions strings
        self.population_size = 20
        self.generations = 5
        self.plan_length = 3

    def generate_plan(self, fitness_function):
        """
        Evolves a sequence of actions that maximizes the fitness function.
        fitness_function: callable(plan) -> score
        """
        # 1. Initialize Population (Random Plans)
        population = []
        for _ in range(self.population_size):
            plan = [random.choice(self.action_space) for _ in range(self.plan_length)]
            population.append(plan)

        best_plan = None
        best_score = -float('inf')

        # 2. Evolution Loop
        for gen in range(self.generations):
            # Evaluate
            scores = []
            for plan in population:
                score = fitness_function(plan)
                scores.append((score, plan))
                if score > best_score:
                    best_score = score
                    best_plan = plan[:]

            # Select Top 50%
            scores.sort(key=lambda x: x[0], reverse=True)
            survivors = [p for s, p in scores[:self.population_size // 2]]

            # Reproduce (Crossover + Mutation)
            new_population = survivors[:]
            while len(new_population) < self.population_size:
                parent = random.choice(survivors)
                child = parent[:]
                
                # Mutate (Change one step)
                if random.random() < 0.3:
                    idx = random.randint(0, self.plan_length - 1)
                    child[idx] = random.choice(self.action_space)
                
                new_population.append(child)
            
            population = new_population

        return best_plan

    def create_mock_fitness(self, goal_description):
        """
        Returns a fitness function based on a text goal (Simple Keyword Matching).
        In a real system, this would use the WorldEngine simulation to predict states.
        """
        def fitness(plan):
            score = 0
            # Example Goal: "explore world"
            if "explore" in goal_description:
                for action in plan:
                    if "move" in action or "look" in action:
                        score += 10
            # Example Goal: "optimize"
            elif "optimize" in goal_description:
                for action in plan:
                    if "optimize" in action or "reflect" in action:
                        score += 10
            return score
        return fitness
