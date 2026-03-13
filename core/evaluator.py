import os
import subprocess
import time

class FitnessEvaluator:
    def __init__(self, project_name, evaluate_fn):
        self.project_name = project_name
        self.evaluate_fn = evaluate_fn

    def evaluate_prompt(self, prompt_text):
        """Runs the provided prompt against the test suite and returns a score."""
        return self.evaluate_fn(prompt_text)

    def evolve(self, prompt_file, iterations=1):
        for i in range(iterations):
            with open(prompt_file, 'r') as f:
                current_prompt = f.read()

            baseline_score = self.evaluate_prompt(current_prompt)
            print(f"[{self.project_name}] Iteration {i+1}: Baseline Score = {baseline_score}")

            # Mock mutation for now
            new_prompt = current_prompt + "\n# Mutated prompt: Focus on high accuracy and clarity."
            
            with open(prompt_file, 'w') as f:
                f.write(new_prompt)

            new_score = self.evaluate_prompt(new_prompt)

            if new_score > baseline_score:
                print(f"[{self.project_name}] Improvement! {baseline_score} -> {new_score}. Committing.")
                subprocess.run(["git", "commit", "-am", f"Evolve {self.project_name} prompt: score {new_score}"], cwd=os.path.dirname(prompt_file))
            else:
                print(f"[{self.project_name}] Degradation. {baseline_score} -> {new_score}. Reverting.")
                subprocess.run(["git", "checkout", "--", os.path.basename(prompt_file)], cwd=os.path.dirname(prompt_file))
