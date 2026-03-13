import os
import subprocess
import time
import random


class FitnessEvaluator:
    def __init__(self, project_name, evaluate_fn):
        self.project_name = project_name
        self.evaluate_fn = evaluate_fn

    def evaluate_prompt(self, prompt_text):
        """Runs the provided prompt against the test suite and returns a score."""
        return self.evaluate_fn(prompt_text)

    def _mutate_prompt(self, current_prompt):
        """Generate a meaningful mutation to the prompt."""
        mutations = [
            " Include specific field extraction details.",
            " Ensure accurate value identification.",
            " Return structured JSON output.",
            " Focus on precision and completeness.",
            " Analyze the document thoroughly.",
            " Extract all relevant data points.",
            " Provide detailed breakdown.",
            " Include confidence scores.",
            " Verify extracted information.",
            " Handle edge cases properly.",
        ]

        # Add mutation based on project type
        if self.project_name == "BuildBid":
            mutation = random.choice(mutations) + " Consider image quality and clarity."
        elif self.project_name == "Trading":
            mutation = random.choice(mutations) + " Include risk metrics."
        else:  # memU
            mutation = random.choice(mutations) + " Optimize for recall."
        # Add mutation based on project type
        if self.project_name == "BuildBid":
            mutation = random.choice(mutations) + " Consider image quality and clarity."
        elif self.project_name == "Trading":
            mutation = random.choice(mutations) + " Include risk metrics."
        elif self.project_name == "memU":
            # memU-specific mutations with required keywords
            memu_mutations = [
                " Search and retrieve relevant memory context.",
                " Find and filter similar memories.",
                " Query the memory store for related information.",
                " Retrieve best matching results from memory.",
                " Lookup memories by category and tags.",
                " Get related context around memory timestamps.",
                " Return top results with filters applied.",
                " Ensure memory store accuracy and completeness.",
            ]
            mutation = random.choice(memu_mutations)
        else:
            mutation = random.choice(mutations)
        # Occasionally prepend instead of append
        if random.random() < 0.3:
            return mutation.strip() + "\n\n" + current_prompt
        return current_prompt + "\n" + mutation

    def evolve(self, prompt_file, iterations=1):
        cwd_path = os.path.dirname(os.path.abspath(prompt_file)) or "."

        for i in range(iterations):
            with open(prompt_file, "r") as f:
                current_prompt = f.read()

            baseline_score = self.evaluate_prompt(current_prompt)
            print(
                f"[{self.project_name}] Iteration {i + 1}/{iterations}: Baseline Score = {baseline_score:.4f}"
            )

            # Generate mutated prompt
            new_prompt = self._mutate_prompt(current_prompt)

            # Evaluate mutated prompt
            new_score = self.evaluate_prompt(new_prompt)
            print(f"[{self.project_name}] Mutation Score = {new_score:.4f}")

            if new_score > baseline_score:
                print(
                    f"[{self.project_name}] ✓ Improvement! {baseline_score:.4f} -> {new_score:.4f}"
                )
                with open(prompt_file, "w") as f:
                    f.write(new_prompt)
                # Commit the improvement
                try:
                    subprocess.run(
                        ["git", "add", os.path.basename(prompt_file)],
                        cwd=cwd_path,
                        capture_output=True,
                    )
                    subprocess.run(
                        [
                            "git",
                            "commit",
                            "-m",
                            f"Evolve {self.project_name} prompt: score {baseline_score:.4f} -> {new_score:.4f}",
                        ],
                        cwd=cwd_path,
                        capture_output=True,
                    )
                    print(f"[{self.project_name}] Committed improvement.")
                except Exception as e:
                    print(f"[{self.project_name}] Git commit failed: {e}")
            elif new_score == baseline_score:
                print(
                    f"[{self.project_name}] = No change, trying different mutation..."
                )
                # Try again with different mutation
                new_prompt = self._mutate_prompt(current_prompt)
                new_score = self.evaluate_prompt(new_prompt)
                if new_score > baseline_score:
                    with open(prompt_file, "w") as f:
                        f.write(new_prompt)
                    try:
                        subprocess.run(
                            ["git", "add", os.path.basename(prompt_file)],
                            cwd=cwd_path,
                            capture_output=True,
                        )
                        subprocess.run(
                            [
                                "git",
                                "commit",
                                "-m",
                                f"Evolve {self.project_name} prompt: score {baseline_score:.4f} -> {new_score:.4f}",
                            ],
                            cwd=cwd_path,
                            capture_output=True,
                        )
                    except:
                        pass
            else:
                print(
                    f"[{self.project_name}] ✗ Degradation. {baseline_score:.4f} -> {new_score:.4f}. Reverting."
                )
                # Don't commit degradation

        print(f"[{self.project_name}] Evolution complete.")
