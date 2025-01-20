import os
import sys
import subprocess
import time
import requests

def get_resource_path(subdir):
    """Devuelve la ruta del subdirectorio empaquetado o relativa en desarrollo."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, subdir)

def esperar_backend(url, timeout=10):
    """Espera hasta que el backend esté disponible."""
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("✅ Backend listo.")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    print("❌ El backend no está listo.")
    return False

def main():
    # Cambia las rutas del backend y frontend
    backend_dir = get_resource_path("backend_flask")
    frontend_dir = get_resource_path("front_pyqt6")

    # Valida que las rutas existan
    if not os.path.isdir(backend_dir):
        print(f"Error: La carpeta del backend no existe: {backend_dir}")
        sys.exit(1)

    if not os.path.isdir(frontend_dir):
        print(f"Error: La carpeta del frontend no existe: {frontend_dir}")
        sys.exit(1)

    # Comandos para ejecutar backend y frontend
    backend_command = ["python", "run.py"]
    frontend_command = ["python", "app.py"]

    print("Iniciando backend...")
    backend = subprocess.Popen(backend_command, cwd=backend_dir)

    if not esperar_backend("http://127.0.0.1:8000/api/test"):
        print("Error: El backend no se inició correctamente.")
        backend.terminate()
        sys.exit(1)

    print("Iniciando frontend...")
    frontend = subprocess.Popen(frontend_command, cwd=frontend_dir)

    print("Ambos procesos están corriendo. Presiona Ctrl+C para salir.")
    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\nCerrando procesos...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    main()
