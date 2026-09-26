#!/usr/bin/env bash

detect_ai_work_hardware() {
  AI_WORK_HW_CPU_CORES="${AI_WORK_DETECTED_CPU_CORES:-$(nproc 2>/dev/null || printf '1')}"
  AI_WORK_HW_RAM_MB="${AI_WORK_DETECTED_RAM_MB:-$(awk '/MemTotal:/ {printf "%d", $2 / 1024}' /proc/meminfo 2>/dev/null)}"
  AI_WORK_HW_RAM_MB="${AI_WORK_HW_RAM_MB:-0}"

  local disk_path="${AI_WORK_HARDWARE_DISK_PATH:-/var/lib/ai-work}"
  [[ -d "$disk_path" ]] || disk_path="/"
  AI_WORK_HW_DISK_MB="${AI_WORK_DETECTED_DISK_MB:-$(df -Pm "$disk_path" 2>/dev/null | awk 'NR == 2 {print $4}')}"
  AI_WORK_HW_DISK_MB="${AI_WORK_HW_DISK_MB:-0}"
  AI_WORK_HW_GPU_NAME="${AI_WORK_DETECTED_GPU_NAME:-Not detected}"
  AI_WORK_HW_GPU_VRAM_MB="${AI_WORK_DETECTED_GPU_VRAM_MB:-0}"
  AI_WORK_HW_CUDA_AVAILABLE="${AI_WORK_DETECTED_CUDA_AVAILABLE:-0}"

  if [[ "${AI_WORK_DETECTED_GPU_VRAM_MB+x}" != "x" ]] && command -v nvidia-smi >/dev/null 2>&1; then
    local gpu_line
    gpu_line="$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null \
      | sort -t, -k2 -nr | head -n 1 || true)"
    if [[ -n "$gpu_line" ]]; then
      AI_WORK_HW_GPU_NAME="$(printf '%s' "$gpu_line" | cut -d, -f1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
      AI_WORK_HW_GPU_VRAM_MB="$(printf '%s' "$gpu_line" | cut -d, -f2 | tr -dc '0-9')"
      AI_WORK_HW_GPU_VRAM_MB="${AI_WORK_HW_GPU_VRAM_MB:-0}"
    fi
  fi
  if [[ "${AI_WORK_DETECTED_CUDA_AVAILABLE+x}" != "x" ]] && command -v nvcc >/dev/null 2>&1; then
    AI_WORK_HW_CUDA_AVAILABLE=1
  fi
}

recommend_ai_work_local_llm() {
  AI_WORK_RECOMMENDED_LLM="none"
  AI_WORK_RECOMMENDATION_REASON="Insufficient free disk or memory for the bundled local models"

  if (( AI_WORK_HW_CUDA_AVAILABLE == 1 && AI_WORK_HW_GPU_VRAM_MB >= 4096 && AI_WORK_HW_DISK_MB >= 5500 )); then
    AI_WORK_RECOMMENDED_LLM="qwen3-4b"
    AI_WORK_RECOMMENDATION_REASON="GPU has at least 4 GB VRAM"
  elif (( AI_WORK_HW_CUDA_AVAILABLE == 1 && AI_WORK_HW_GPU_VRAM_MB >= 2560 && AI_WORK_HW_DISK_MB >= 4700 )); then
    AI_WORK_RECOMMENDED_LLM="qwen3-1.7b"
    AI_WORK_RECOMMENDATION_REASON="GPU VRAM is better suited to the balanced model"
  elif (( AI_WORK_HW_CUDA_AVAILABLE == 1 && AI_WORK_HW_GPU_VRAM_MB >= 1536 && AI_WORK_HW_DISK_MB >= 3500 )); then
    AI_WORK_RECOMMENDED_LLM="qwen3-0.6b"
    AI_WORK_RECOMMENDATION_REASON="GPU VRAM is best suited to the compact model"
  elif (( AI_WORK_HW_RAM_MB >= 12288 && AI_WORK_HW_DISK_MB >= 5500 )); then
    AI_WORK_RECOMMENDED_LLM="qwen3-4b"
    AI_WORK_RECOMMENDATION_REASON="System RAM supports CPU inference with Qwen3 4B"
  elif (( AI_WORK_HW_RAM_MB >= 6144 && AI_WORK_HW_DISK_MB >= 4700 )); then
    AI_WORK_RECOMMENDED_LLM="qwen3-1.7b"
    AI_WORK_RECOMMENDATION_REASON="System RAM supports balanced CPU inference"
  elif (( AI_WORK_HW_RAM_MB >= 3072 && AI_WORK_HW_DISK_MB >= 3500 )); then
    AI_WORK_RECOMMENDED_LLM="qwen3-0.6b"
    AI_WORK_RECOMMENDATION_REASON="System RAM supports compact CPU inference"
  fi
}

print_ai_work_hardware_recommendation() {
  printf '\nDetected server hardware\n'
  printf '  CPU cores:       %s\n' "$AI_WORK_HW_CPU_CORES"
  printf '  System RAM:      %s MB\n' "$AI_WORK_HW_RAM_MB"
  printf '  Free disk:       %s MB\n' "$AI_WORK_HW_DISK_MB"
  printf '  NVIDIA GPU:      %s\n' "$AI_WORK_HW_GPU_NAME"
  printf '  GPU VRAM:        %s MB\n' "$AI_WORK_HW_GPU_VRAM_MB"
  if [[ "$AI_WORK_HW_CUDA_AVAILABLE" == "1" ]]; then
    printf '  CUDA toolkit:    available\n'
  elif (( AI_WORK_HW_GPU_VRAM_MB > 0 )); then
    printf '  CUDA toolkit:    not found; local LLM will use CPU unless CUDA is installed\n'
  else
    printf '  CUDA toolkit:    not detected\n'
  fi
  printf '  Recommendation:  %s (%s)\n' "$AI_WORK_RECOMMENDED_LLM" "$AI_WORK_RECOMMENDATION_REASON"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  detect_ai_work_hardware
  recommend_ai_work_local_llm
  print_ai_work_hardware_recommendation
fi
