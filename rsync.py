import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

origem = "caminho da origem"
destino = "caminho do destino"
usuario = "root"
hostname = "ip"
log_file = "caminho arquivo de log"

def sincronizar_pastas():
    rsync_comando = (
        f'rsync -azP --itemize-changes '
        f'{origem} {usuario}@{hostname}:{destino}'
    )
    try:
        resultado = subprocess.run(rsync_comando, check=True, text=True, capture_output=True, shell=True)
        print(resultado.stdout)

        if '100%' in resultado.stdout:
            result = '100% concluído'
        else:
            result = 'Erro: sincronização não concluída'

        filtrar_log(resultado.stdout, result)
    except subprocess.CalledProcessError as e:
        print(f'Erro ao executar rsync: {e}')

def filtrar_log(log, result):
    with open(log_file, 'a') as f:
        for line in log.splitlines():
            if line.startswith(('>f', '>d', '<f', 'deleting', '<d')):
                if line.startswith('<f'):
                    f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")}: Arquivo recebido - {line} : {result}\n')

class SincronizarHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'Modificação detectada: {event.src_path}')
        sincronizar_pastas()

    def on_created(self, event):
        print(f'Arquivo criado: {event.src_path}')
        sincronizar_pastas()

    def on_deleted(self, event):
        print(f'Arquivo excluído: {event.src_path}')
        sincronizar_pastas()

if __name__ == "__main__":
    event_handler = SincronizarHandler()
    observer = Observer()
    observer.schedule(event_handler, path=origem, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
