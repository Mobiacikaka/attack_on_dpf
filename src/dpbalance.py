import math
import random
from collections import defaultdict

# A small epsilon to prevent division by zero in the utility function
EPSILON = 1e-6

class DataBlock:
	"""Represents a data block with a given privacy budget."""
	def __init__(self, block_id, privacy_budget):
		self.block_id = block_id
		self.privacy_budget = privacy_budget
		self.is_used = False

class DataAnalyst:
	"""Represents a data analyst with multiple training pipelines."""
	def __init__(self, analyst_id, pipelines):
		self.analyst_id = analyst_id
		self.pipelines = pipelines
		self.allocated_budget = 0
		self.waiting_time = 0

class Pipeline:
	"""Represents a single training pipeline request."""
	def __init__(self, pipeline_id, demand, data_match_score=1.0, training_loss=0.1):
		self.pipeline_id = pipeline_id
		self.demand = demand
		self.data_match_score = data_match_score
		self.training_loss = training_loss
		self.is_allocated = False

class DPBalanceScheduler:
	"""
	Implements the DPBalance privacy budget scheduling mechanism.
	"""
	def __init__(self, lambda_param, beta_param):
		self.lambda_param = lambda_param
		self.beta_param = beta_param

	def calculate_analyst_utility(self, analyst, total_budget):
		"""Calculates the utility for a single data analyst."""
		if total_budget == 0:
			return 0
		# Simplistic T(t) function: 1 / (1 + waiting_time)
		# dominant share, weighted by the data-pipeline matching degree
		# Pipeline delay time means how long a pipeline has been waiting since it proposes training demand
		waiting_time_factor = 1.0 / (1.0 + analyst.waiting_time)
		dominant_share = analyst.allocated_budget / total_budget
		efficiency = dominant_share * waiting_time_factor * (1.0 - analyst.pipelines[0].training_loss) # Simplified for a single pipeline
		return efficiency

	def calculate_total_utility(self, analysts, total_budget):
		"""Calculates the platform's total utility based on efficiency and fairness."""
		if total_budget == 0:
			return 0

		# Calculate individual analyst utilities
		analyst_utilities = [self.calculate_analyst_utility(a, total_budget) for a in analysts]

		# Calculate dominant efficiency (sum of analyst utilities)
		dominant_efficiency = sum(analyst_utilities)

		# Calculate dominant fairness
		dominant_fairness_term = 0
		if dominant_efficiency > EPSILON:
			for utility in analyst_utilities:
				dominant_fairness_term += (utility / dominant_efficiency) ** (1 - self.beta_param)

		if self.beta_param == 1:
			dominant_fairness = math.log(dominant_fairness_term + EPSILON)
		else:
			dominant_fairness = dominant_fairness_term ** (1 / self.beta_param)

		# Combine fairness and efficiency for the final platform utility
		platform_utility = dominant_fairness * (dominant_efficiency ** self.lambda_param)
		return platform_utility

	def run_scheduling(self, data_analysts, data_blocks):
		"""
		Simulates the sequential allocation mechanism of DPBalance.
		
		This is a simplified implementation of the core logic, focusing on the
		sequential allocation and utility calculation described in the paper.
		The paper uses more complex methods like Lagrange multipliers and
		greedy heuristics; this code approximates that behavior.
		"""
		print("Starting DPBalance scheduling simulation...")
		
		# Step 1: Data Block Information Collection
		total_privacy_budget = sum(block.privacy_budget for block in data_blocks)
		
		print(f"Total available privacy budget: {total_privacy_budget}")
		
		# Step 2 & 3: Sequential Allocation (simplified)
		# This part approximates the Lagrange multiplier method
		
		# Initialize allocations
		for analyst in data_analysts:
			analyst.allocated_budget = 0
		
		remaining_budget = total_privacy_budget
		
		# Sort analysts by a simple heuristic (e.g., total demand)
		data_analysts.sort(key=lambda a: sum(p.demand for p in a.pipelines), reverse=True)
		
		while remaining_budget > 0 and any(a.allocated_budget < sum(p.demand for p in a.pipelines) for a in data_analysts):
			for analyst in data_analysts:
				pipeline_demand = sum(p.demand for p in analyst.pipelines)
				if analyst.allocated_budget < pipeline_demand and remaining_budget > 0:
					# Allocate a small portion of budget to each analyst in turn
					allocation_amount = min(remaining_budget, 1.0) # A small, fixed amount
					analyst.allocated_budget += allocation_amount
					remaining_budget -= allocation_amount

		print("\n--- Allocation Results ---")
		for analyst in data_analysts:
			print(f"Data Analyst {analyst.analyst_id}: Allocated Budget = {analyst.allocated_budget:.2f}")

		# Step 4: Pipeline-level Allocation (greedy heuristics)
		print("\n--- Pipeline Execution ---")
		for analyst in data_analysts:
			remaining_analyst_budget = analyst.allocated_budget
			
			# Sort pipelines by demand (greedy approach: satisfy smallest first)
			analyst.pipelines.sort(key=lambda p: p.demand)
			
			for pipeline in analyst.pipelines:
				if remaining_analyst_budget >= pipeline.demand:
					pipeline.is_allocated = True
					remaining_analyst_budget -= pipeline.demand
					print(f"  - Pipeline {pipeline.pipeline_id} from Analyst {analyst.analyst_id} is executed.")
				else:
					print(f"  - Pipeline {pipeline.pipeline_id} from Analyst {analyst.analyst_id} cannot be executed due to insufficient budget.")

		# Step 5: Calculate Final Utility
		final_utility = self.calculate_total_utility(data_analysts, total_privacy_budget)
		print(f"\nFinal Platform Utility: {final_utility:.4f}")

if __name__ == '__main__':
	# Define simulation parameters
	NUM_ANALYSTS = 3
	NUM_PIPELINES_PER_ANALYST = 2
	TOTAL_BUDGET = 50
	DATA_BLOCKS_NUM = 5
	DATA_BLOCKS_BUDGET = TOTAL_BUDGET / DATA_BLOCKS_NUM

	# Create data blocks (simplified)
	data_blocks = [DataBlock(i, DATA_BLOCKS_BUDGET) for i in range(DATA_BLOCKS_NUM)]

	# Create data analysts and their pipelines
	data_analysts = []
	for i in range(NUM_ANALYSTS):
		pipelines = [Pipeline(
			pipeline_id=f'{i}-{j}',
			demand=random.randint(5, 15) # Varying demands
		) for j in range(NUM_PIPELINES_PER_ANALYST)]
		for pipeline in pipelines:
			print(f" - Pipeline {pipeline.demand}")
		analyst = DataAnalyst(analyst_id=i, pipelines=pipelines)
		data_analysts.append(analyst)

	# Set parameters for fairness (beta) and efficiency (lambda)
	# A higher lambda favors efficiency, a higher beta favors fairness
	scheduler = DPBalanceScheduler(lambda_param=0.5, beta_param=0.8)

	scheduler.run_scheduling(data_analysts, data_blocks)

