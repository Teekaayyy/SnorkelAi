"""Runtime pipeline options and toggles."""

# If True, skip a stage if its output already exists (idempotent runs)
SKIP_IF_EXISTS = False

# If True, validate output dimensions and format after each stage
VALIDATE_AFTER_EACH_STAGE = True

# Supported input extensions
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}