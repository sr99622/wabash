#!/bin/bash
#
# Ensure core dumps are enabled and redirected to a known directory
#

# --- CONFIGURABLE SECTION ---
CORE_DIR="$HOME/core_dumps"
CORE_PATTERN="$CORE_DIR/core.%e.%p.%t"
PYTHON_SCRIPT="/home/stephen/wabash/gui/main.py"   # change this line if needed
# -----------------------------

echo "==> Setting up core dump environment..."

# 1. Create the directory if it doesn’t exist
mkdir -p "$CORE_DIR"
chmod 1777 "$CORE_DIR"   # world-writable with sticky bit (like /tmp)

# 2. Enable unlimited core dump size for this session
ulimit -c unlimited
echo "   Core dump size limit set to unlimited."

# 3. Set the system core pattern (requires sudo)
if [ "$(id -u)" -ne 0 ]; then
    echo "   Asking for sudo to set core pattern..."
    echo "$CORE_PATTERN" | sudo tee /proc/sys/kernel/core_pattern > /dev/null
else
    echo "$CORE_PATTERN" > /proc/sys/kernel/core_pattern
fi

# 4. Print current settings for confirmation
echo "   Core pattern now set to: $(cat /proc/sys/kernel/core_pattern)"
echo "   Core dumps will be written to: $CORE_DIR"
echo "-----------------------------------------"

# 5. Run your program (in this case, Python)
python3 "$PYTHON_SCRIPT"

# 6. After crash, show where dumps are located
echo "-----------------------------------------"
echo "If a segmentation fault occurs, check for core dumps in:"
echo "   $CORE_DIR"
ls -lh "$CORE_DIR"
