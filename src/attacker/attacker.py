from scheduler.dpf import DPFScheduler
from scheduler.pipeline import Pipeline

class BasicAttacker:
	"""
	Basic Attacker
		DO NOTHING WHEN ATTACKING
	"""

	def __init__(self, scheduler: DPFScheduler, NumAtkPL: int) -> None:
		self.NumAtkPL: int = NumAtkPL

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		"""
		Main Attack Function
		"""

		## DO NOTHING
		return None
