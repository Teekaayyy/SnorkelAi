#!/usr/bin/env bash
mkdir -p /logs/verifier

cd /service

echo "=== PYTHONPATH: $PYTHONPATH ==="
echo "=== Files in /service/app/math/ ==="
ls /service/app/math/
echo "=== scalar_ops.py quadratic_cost line ==="
grep "quadratic_cost\|return sum" /service/app/math/scalar_ops.py
echo "=== Running simulation test ==="
python -c "
import sys
sys.path.insert(0, '/service')
from app.core.config import ChallengeConfig
from app.utils.simulation import ClosedLoopSimulation
cfg = ChallengeConfig()
sim = ClosedLoopSimulation(cfg)
logger = sim.run()
print('samples:', len(logger.rows))
print('max_theta:', max(abs(r.theta) for r in logger.rows))
" 2>&1

pip install -q pytest==8.4.1 pytest-json-ctrf==0.3.5

python -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi