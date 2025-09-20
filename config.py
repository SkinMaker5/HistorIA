from pathlib import Path

VAULT_DIR = Path(__file__).parent / "HistorIA_Vault"

CHAR_DIR = VAULT_DIR / "characters"
LOC_DIR  = VAULT_DIR / "locations"
SCEN_DIR = VAULT_DIR / "scenarios"

# AI model
MODEL = "hf.co/tensorblock/pygmalion-7b-GGUF:Q4_K_M"

# Generation parameters
GPU_ENABLED = False
MAX_TOKENS = 300

# World memory
WORLD_STATE_FILE = VAULT_DIR / "WorldState.json"

