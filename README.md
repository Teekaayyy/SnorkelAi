# adaptive-mpc-debugger

Debugging task: fix a broken nonlinear cart-pole adaptive MPC control system.

The codebase implements a sampling-based Model Predictive Controller with an Extended Kalman Filter estimator. Multiple modules contain logic errors that prevent the controller from stabilising the pole for the full 10-second simulation.

## Running

```bash
cd /service
python -m app.main
```

## Testing

```bash
pytest /tests/test_outputs.py -rA
```
