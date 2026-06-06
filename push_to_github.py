import os
import subprocess
import sys
from pathlib import Path

WORKDIR = Path(__file__).resolve().parent
GIT_PATHS = [
    Path(r"C:\Program Files\Git\cmd\git.exe"),
    Path(r"C:\Program Files\Git\bin\git.exe"),
    Path(r"C:\Program Files (x86)\Git\cmd\git.exe"),
    Path(r"C:\Program Files (x86)\Git\bin\git.exe"),
]


def find_git() -> Path:
    for path in GIT_PATHS:
        if path.exists():
            return path
    raise FileNotFoundError('No se encontró git en rutas conocidas. Instala Git y vuelve a ejecutar este script.')


def run_git(args, check=True):
    git = find_git()
    result = subprocess.run([str(git)] + args, cwd=WORKDIR, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stdout}\n{result.stderr}")
    return result


if __name__ == '__main__':
    token = None
    if len(sys.argv) >= 2:
        token = sys.argv[1].strip()
    if not token:
        token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print('Uso: python push_to_github.py <GITHUB_PAT>')
        sys.exit(1)

    print('Usando git en:', find_git())

    if not (WORKDIR / '.git').exists():
        print('Inicializando repo git local...')
        run_git(['init'])
    else:
        print('Repo git existente detectado.')

    print('Configurando autor git local...')
    run_git(['config', '--local', 'user.email', 'actions@github.com'])
    run_git(['config', '--local', 'user.name', 'Automated Push'])

    print('Agregando archivos...')
    run_git(['add', '.'])

    try:
        print('Haciendo commit...')
        run_git(['commit', '-m', 'Add project and CI workflow'])
    except RuntimeError as exc:
        error_text = str(exc).lower()
        if 'nothing to commit' in error_text or 'no changes added to commit' in error_text:
            print('No hay cambios nuevos para commitear.')
        else:
            raise

    print('Asegurando rama main...')
    run_git(['branch', '-M', 'main'])
    run_git(['remote', 'remove', 'origin'], check=False)

    remote_url = f'https://{token}@github.com/ggilmer25-hue/android_vmc.git'
    print('Configurando remoto...')
    run_git(['remote', 'add', 'origin', remote_url])

    print('Empujando a GitHub...')
    result = run_git(['push', '-u', 'origin', 'main', '--force'])
    print(result.stdout)
    print(result.stderr)
    print('Push completado. Verifica la ejecución de Actions en https://github.com/ggilmer25-hue/android_vmc/actions')
