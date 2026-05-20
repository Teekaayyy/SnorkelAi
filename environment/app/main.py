"""
main.py
=======
Entry point for the adaptive MPC cart-pole challenge.

Usage:
    python -m app.main
"""
from app.core.config import ChallengeConfig
from app.utils.simulation import ClosedLoopSimulation


def main() -> None:
    cfg = ChallengeConfig()
    sim = ClosedLoopSimulation(cfg)
    logger = sim.run()
    logger.write_csv("/service/output/telemetry.csv")
    print(logger.summary())


if __name__ == "__main__":
    main()
