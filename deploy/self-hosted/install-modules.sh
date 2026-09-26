#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/opt/ai-work"
STATE_DIR="/var/lib/ai-work"
CONFIG_FILE="/etc/ai-work/ai-work.env"
SYSTEMD_DIR="/etc/systemd/system"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

[[ "$(uname -s)" == "Linux" ]] || fail "This installer supports Ubuntu Linux only."
[[ "${EUID:-$(id -u)}" == "0" ]] || fail "Run this installer with sudo."
[[ -f "$CONFIG_FILE" ]] || fail "Install AI Work Core before optional modules."

is_enabled() {
  case "${1:-}" in
    1|true|TRUE|yes|YES|on|ON) return 0 ;;
    *) return 1 ;;
  esac
}

set_config() {
  local key="$1" value="$2"
  if grep -q "^${key}=" "$CONFIG_FILE"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$CONFIG_FILE"
  else
    printf '%s=%s\n' "$key" "$value" >> "$CONFIG_FILE"
  fi
}

require_disk_mb() {
  local required_mb="$1" label="$2" available_kb
  available_kb="$(df -Pk "$STATE_DIR" | awk 'NR == 2 {print $4}')"
  if (( available_kb < required_mb * 1024 )); then
    fail "$label requires about ${required_mb} MB free; only $((available_kb / 1024)) MB is available."
  fi
}

install_packages() {
  apt-get update
  apt-get install -y --no-install-recommends "$@"
}

profile="${AI_WORK_INSTALL_PROFILE:-}"
if [[ -z "$profile" && -t 0 ]]; then
  printf '\nOptional AI modules\n'
  printf 'PDF and DOCX parsing are already included in AI Work Core.\n'
  printf '  1) Core only       No additional model downloads\n'
  printf '  2) Knowledge       PaddleOCR + Qwen3 Embedding (recommended)\n'
  printf '  3) Meetings        whisper.cpp small + Qwen3 Embedding\n'
  printf '  4) Complete        OCR + Embedding + Whisper + optional local LLM\n'
  printf '  5) Custom          Select each module\n'
  read -r -p 'Select [2]: ' profile_choice
  case "${profile_choice:-2}" in
    1) profile="core" ;;
    2) profile="knowledge" ;;
    3) profile="meeting" ;;
    4) profile="complete" ;;
    5) profile="custom" ;;
    *) fail "Unknown profile: $profile_choice" ;;
  esac
fi
profile="${profile:-core}"

install_ocr=0
install_embedding=0
install_whisper=0
local_llm="${AI_WORK_LOCAL_LLM:-none}"

case "$profile" in
  core|keep) ;;
  knowledge) install_ocr=1; install_embedding=1 ;;
  meeting) install_embedding=1; install_whisper=1 ;;
  complete) install_ocr=1; install_embedding=1; install_whisper=1 ;;
  custom) ;;
  *) fail "AI_WORK_INSTALL_PROFILE must be core, knowledge, meeting, complete, custom, or keep." ;;
esac

if [[ "$profile" == "custom" && -t 0 ]]; then
  read -r -p 'Install PaddleOCR? [y/N]: ' answer
  is_enabled "$answer" && install_ocr=1
  read -r -p 'Install Qwen3 Embedding 0.6B CPU service? [Y/n]: ' answer
  [[ -z "$answer" ]] || ! is_enabled "$answer" || install_embedding=1
  [[ -z "$answer" ]] && install_embedding=1
  read -r -p 'Install whisper.cpp small? [y/N]: ' answer
  is_enabled "$answer" && install_whisper=1
fi

is_enabled "${AI_WORK_INSTALL_OCR:-}" && install_ocr=1
is_enabled "${AI_WORK_INSTALL_EMBEDDING:-}" && install_embedding=1
is_enabled "${AI_WORK_INSTALL_WHISPER:-}" && install_whisper=1

if [[ "$profile" == "complete" || "$profile" == "custom" ]]; then
  if [[ "${AI_WORK_LOCAL_LLM+x}" != "x" && -t 0 ]]; then
    printf '\nLocal LLM (served only on 127.0.0.1:8080)\n'
    printf '  1) None\n'
    printf '  2) Qwen3 0.6B Q8_0  about 0.7 GB, CPU-friendly\n'
    printf '  3) Qwen3 1.7B Q8_0  about 1.9 GB, balanced\n'
    printf '  4) Qwen3 4B Q4_K_M about 2.6 GB, recommended with 8 GB+ RAM\n'
    read -r -p 'Select [1]: ' llm_choice
    case "${llm_choice:-1}" in
      1) local_llm="none" ;;
      2) local_llm="qwen3-0.6b" ;;
      3) local_llm="qwen3-1.7b" ;;
      4) local_llm="qwen3-4b" ;;
      *) fail "Unknown local LLM choice: $llm_choice" ;;
    esac
  fi
fi

printf '\nInstallation plan: OCR=%s Embedding=%s Whisper=%s Local-LLM=%s\n' \
  "$install_ocr" "$install_embedding" "$install_whisper" "$local_llm"

if [[ "$install_ocr" == "1" ]]; then
  require_disk_mb 3500 "PaddleOCR"
  printf '\nInstalling PaddleOCR...\n'
  "$INSTALL_DIR/.venv/bin/python" -m pip install -r "$INSTALL_DIR/requirements-ocr.txt"
fi

if [[ "$install_embedding" == "1" ]]; then
  require_disk_mb 5000 "Qwen3 Embedding"
  printf '\nInstalling Qwen3 Embedding CPU service...\n'
  if [[ ! -d "$INSTALL_DIR/.venv-embedding" ]]; then
    python3 -m venv "$INSTALL_DIR/.venv-embedding"
  fi
  "$INSTALL_DIR/.venv-embedding/bin/python" -m pip install --upgrade pip wheel
  "$INSTALL_DIR/.venv-embedding/bin/python" -m pip install -r "$INSTALL_DIR/requirements-embedding.txt"
  install -d -o aiwork -g aiwork -m 0750 "$STATE_DIR/storage/models/huggingface"
  runuser -u aiwork -- env HF_HOME="$STATE_DIR/storage/models/huggingface" \
    "$INSTALL_DIR/.venv-embedding/bin/hf" download Qwen/Qwen3-Embedding-0.6B
  install -o root -g root -m 0644 \
    "$INSTALL_DIR/deploy/self-hosted/ai-work-embedding.service" \
    "$SYSTEMD_DIR/ai-work-embedding.service"
  systemctl daemon-reload
  systemctl enable --now ai-work-embedding.service
fi

if [[ "$install_whisper" == "1" ]]; then
  require_disk_mb 1800 "whisper.cpp small"
  printf '\nInstalling whisper.cpp small...\n'
  install_packages build-essential cmake git
  install -d -o root -g root -m 0755 "$INSTALL_DIR/runtime"
  if [[ ! -d "$INSTALL_DIR/runtime/whisper.cpp/.git" ]]; then
    git clone --depth 1 https://github.com/ggml-org/whisper.cpp.git "$INSTALL_DIR/runtime/whisper.cpp"
  else
    git -C "$INSTALL_DIR/runtime/whisper.cpp" pull --ff-only
  fi
  cmake -S "$INSTALL_DIR/runtime/whisper.cpp" -B "$INSTALL_DIR/runtime/whisper.cpp/build" \
    -DWHISPER_CURL=OFF -DGGML_CUDA=OFF
  cmake --build "$INSTALL_DIR/runtime/whisper.cpp/build" --config Release -j "$(nproc)" --target whisper-cli
  install -d -o aiwork -g aiwork -m 0750 "$STATE_DIR/storage/models/whisper"
  "$INSTALL_DIR/runtime/whisper.cpp/models/download-ggml-model.sh" small "$STATE_DIR/storage/models/whisper"
  chown aiwork:aiwork "$STATE_DIR/storage/models/whisper/ggml-small.bin"
  set_config WHISPER_CPP_BIN "$INSTALL_DIR/runtime/whisper.cpp/build/bin/whisper-cli"
  set_config WHISPER_CPP_MODEL "$STATE_DIR/storage/models/whisper/ggml-small.bin"
  set_config WHISPER_CPP_USE_GPU 0
fi

case "$local_llm" in
  none|"") ;;
  qwen3-0.6b)
    llm_repo="Qwen/Qwen3-0.6B-GGUF"
    llm_file="Qwen3-0.6B-Q8_0.gguf"
    llm_size_mb=900
    ;;
  qwen3-1.7b)
    llm_repo="Qwen/Qwen3-1.7B-GGUF"
    llm_file="Qwen3-1.7B-Q8_0.gguf"
    llm_size_mb=2200
    ;;
  qwen3-4b)
    llm_repo="Qwen/Qwen3-4B-GGUF"
    llm_file="Qwen3-4B-Q4_K_M.gguf"
    llm_size_mb=3000
    ;;
  *) fail "AI_WORK_LOCAL_LLM must be none, qwen3-0.6b, qwen3-1.7b, or qwen3-4b." ;;
esac

if [[ "$local_llm" != "none" && -n "$local_llm" ]]; then
  require_disk_mb $((llm_size_mb + 2500)) "$local_llm"
  printf '\nInstalling llama.cpp and %s...\n' "$local_llm"
  install_packages build-essential cmake git
  install -d -o root -g root -m 0755 "$INSTALL_DIR/runtime"
  if [[ ! -d "$INSTALL_DIR/runtime/llama.cpp/.git" ]]; then
    git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$INSTALL_DIR/runtime/llama.cpp"
  else
    git -C "$INSTALL_DIR/runtime/llama.cpp" pull --ff-only
  fi
  cmake_args=()
  gpu_layers=0
  if is_enabled "${AI_WORK_LLAMA_CUDA:-}"; then
    command -v nvcc >/dev/null 2>&1 || fail "AI_WORK_LLAMA_CUDA=1 requires the NVIDIA CUDA toolkit (nvcc)."
    cmake_args+=("-DGGML_CUDA=ON")
    gpu_layers=99
  fi
  cmake -S "$INSTALL_DIR/runtime/llama.cpp" -B "$INSTALL_DIR/runtime/llama.cpp/build" "${cmake_args[@]}"
  cmake --build "$INSTALL_DIR/runtime/llama.cpp/build" --config Release -j "$(nproc)" --target llama-server
  install -d -o aiwork -g aiwork -m 0750 "$STATE_DIR/storage/models/llm"
  model_path="$STATE_DIR/storage/models/llm/$llm_file"
  curl --fail --location --continue-at - --progress-bar \
    "https://huggingface.co/${llm_repo}/resolve/main/${llm_file}?download=true" \
    --output "$model_path"
  chown aiwork:aiwork "$model_path"
  umask 027
  printf 'LLAMA_MODEL_PATH=%s\nLLAMA_MODEL_ALIAS=%s\nLLAMA_GPU_LAYERS=%s\nLLAMA_CONTEXT_SIZE=4096\n' \
    "$model_path" "$local_llm" "$gpu_layers" > /etc/ai-work/local-llm.env
  chown root:aiwork /etc/ai-work/local-llm.env
  install -o root -g root -m 0644 \
    "$INSTALL_DIR/deploy/self-hosted/ai-work-llm.service" \
    "$SYSTEMD_DIR/ai-work-llm.service"
  set_config AI_WORK_DEFAULT_LLM_MODEL_ID "local:$local_llm"
  systemctl daemon-reload
  systemctl enable --now ai-work-llm.service
fi

chown root:aiwork "$CONFIG_FILE"
chmod 0640 "$CONFIG_FILE"
systemctl restart ai-work.service

printf '\nOptional module setup completed.\n'
systemctl --no-pager --plain --type=service --state=running \
  ai-work.service ai-work-embedding.service ai-work-llm.service 2>/dev/null || true
