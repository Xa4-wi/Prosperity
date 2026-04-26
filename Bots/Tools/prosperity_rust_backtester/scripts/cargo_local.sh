#!/bin/sh
set -eu

os_name="$(uname -s)"
clean_path="${HOME}/.cargo/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
clt_python_lib="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib"
xcode_python_lib="/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib"
clt_python_frameworks="/Library/Developer/CommandLineTools/Library/Frameworks"
xcode_python_frameworks="/Applications/Xcode.app/Contents/Developer/Library/Frameworks"

effective_target_dir() {
    if [ -n "${CARGO_TARGET_DIR-}" ]; then
        printf '%s\n' "${CARGO_TARGET_DIR}"
        return
    fi

    case "${os_name}" in
        Darwin) printf '%s\n' "${HOME}/Library/Caches/rust_backtester/target" ;;
        *) printf '\n' ;;
    esac
}

case "${1-}" in
    --print-target-dir)
        effective_target_dir
        exit 0
        ;;
    --print-clean-path)
        printf '%s\n' "${clean_path}"
        exit 0
        ;;
esac

if [ "${os_name}" != "Darwin" ]; then
    exec cargo "$@"
fi

target_dir="$(effective_target_dir)"
if [ -n "${target_dir}" ]; then
    mkdir -p "${target_dir}"
fi

if [ -n "${PYO3_PYTHON-}" ]; then
    pyo3_python="${PYO3_PYTHON}"
else
    pyo3_python="$(command -v python3 2>/dev/null || printf '%s\n' python3)"
fi

effective_library_path="${LIBRARY_PATH-}"
if [ ! -d "${xcode_python_lib}" ] && [ -d "${clt_python_lib}" ]; then
    if [ -n "${effective_library_path}" ]; then
        effective_library_path="${clt_python_lib}:${effective_library_path}"
    else
        effective_library_path="${clt_python_lib}"
    fi
fi

effective_framework_path="${DYLD_FALLBACK_FRAMEWORK_PATH-}"
if [ ! -d "${xcode_python_frameworks}" ] && [ -d "${clt_python_frameworks}" ]; then
    if [ -n "${effective_framework_path}" ]; then
        effective_framework_path="${clt_python_frameworks}:${effective_framework_path}"
    else
        effective_framework_path="${clt_python_frameworks}"
    fi
fi

exec env -i \
    HOME="${HOME}" \
    USER="${USER-}" \
    LOGNAME="${LOGNAME-${USER-}}" \
    PATH="${clean_path}" \
    TMPDIR="${TMPDIR-/tmp}" \
    TERM="${TERM-dumb}" \
    CARGO_TARGET_DIR="${target_dir}" \
    ${CARGO_HOME+"CARGO_HOME=${CARGO_HOME}"} \
    ${RUSTUP_HOME+"RUSTUP_HOME=${RUSTUP_HOME}"} \
    ${HTTP_PROXY+"HTTP_PROXY=${HTTP_PROXY}"} \
    ${HTTPS_PROXY+"HTTPS_PROXY=${HTTPS_PROXY}"} \
    ${NO_PROXY+"NO_PROXY=${NO_PROXY}"} \
    ${SSL_CERT_FILE+"SSL_CERT_FILE=${SSL_CERT_FILE}"} \
    ${SSL_CERT_DIR+"SSL_CERT_DIR=${SSL_CERT_DIR}"} \
    ${effective_library_path+"LIBRARY_PATH=${effective_library_path}"} \
    ${effective_framework_path+"DYLD_FALLBACK_FRAMEWORK_PATH=${effective_framework_path}"} \
    PYO3_PYTHON="${pyo3_python}" \
    cargo "$@"
