#!/usr/bin/env bash
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-dwirx/duckse}"
BIN_NAME="duckse"
INSTALL_DIR="${INSTALL_DIR:-}"
VERSION="${1:-latest}"

if [[ -z "$INSTALL_DIR" ]]; then
  if [[ -w "/usr/local/bin" ]]; then
    INSTALL_DIR="/usr/local/bin"
  else
    INSTALL_DIR="${HOME}/.local/bin"
  fi
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl tidak ditemukan." >&2
  exit 1
fi

if ! command -v tar >/dev/null 2>&1; then
  echo "Error: tar tidak ditemukan." >&2
  exit 1
fi

OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$OS" in
  linux*)  PLATFORM="linux" ;;
  darwin*) PLATFORM="macos" ;;
  *)
    echo "Error: OS '$OS' belum didukung installer ini." >&2
    exit 1
    ;;
esac

case "$ARCH" in
  x86_64|amd64) ARCH="x86_64" ;;
  *)
    echo "Error: Arsitektur '$ARCH' belum didukung installer ini. Saat ini hanya x86_64/amd64." >&2
    exit 1
    ;;
esac

if [[ "$VERSION" == "latest" ]]; then
  TAG="$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | sed -n 's/.*"tag_name": "\([^"]*\)".*/\1/p' | head -n1)"
  if [[ -z "$TAG" ]]; then
    echo "Error: gagal membaca release terbaru dari ${REPO}." >&2
    exit 1
  fi
else
  TAG="$VERSION"
fi

ASSET="${BIN_NAME}-${PLATFORM}-${ARCH}.tar.gz"
URL="https://github.com/${REPO}/releases/download/${TAG}/${ASSET}"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

echo "Downloading ${URL}"
curl -fL "$URL" -o "$tmpdir/$ASSET"
tar -xzf "$tmpdir/$ASSET" -C "$tmpdir"

mkdir -p "$INSTALL_DIR"

install_target="$INSTALL_DIR/$BIN_NAME"
if [[ -w "$INSTALL_DIR" ]]; then
  install -m 0755 "$tmpdir/$BIN_NAME" "$install_target"
else
  if command -v sudo >/dev/null 2>&1; then
    sudo install -m 0755 "$tmpdir/$BIN_NAME" "$install_target"
  else
    echo "Error: tidak punya izin menulis ke $INSTALL_DIR dan sudo tidak tersedia." >&2
    exit 1
  fi
fi

echo "Installed: $install_target"
if ! command -v "$BIN_NAME" >/dev/null 2>&1; then
  echo "Catatan: tambahkan $INSTALL_DIR ke PATH jika perintah '$BIN_NAME' belum dikenali."
fi
