import os
from os import walk, path
import ntpath
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

abspath = path.abspath(__file__)
dir_script = path.dirname(abspath)

# Es la cantidad de bytes máxima que tendrán las carpetas separadas
tamano_maximo_parte = 15*1048576

# Directorio donde se van a crear las carpetas particionadas
dir_salida = path.join(dir_script, 'PARTES_SEPARADAS')

# Archivo que permite revertir la ubicación de los archivos separados.
# fecha_hora = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
# archivo_revertir = path.join(dir_script, f'restaurar_{fecha_hora}.bat')
archivo_revertir = path.join(dir_script, f'restaurar.bat')

# Inicialización del logging
archivo_log = path.splitext(abspath)[0] + '.log'
handler = RotatingFileHandler(archivo_log, maxBytes=1048576*50, backupCount=1, encoding='utf8')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s")
        # "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")

handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Empieza por la carpeta "parte1"
parte_actual = 1

# Bytes acumulados en la parte actual
acum_actual = 0

# Lista de los directorios que fueron creados 
# en la ejecución de este programa
directorios_creados = []

# Lista de archivos movidos a las carpetas de partes
# por este programa
archivos_movidos = []

# Mueve un archivo a la carpeta de parte que le corresponde
# dentro del directorio de salida.
def mover(ruta_f):
    dir_relativo = path.relpath(path.dirname(ruta_f), start = dir_script)
    ruta_f_destino = path.join(dir_salida, f'PARTE{parte_actual}' , dir_relativo, ntpath.basename(ruta_f))
    dir_origen = path.join(dir_script, dir_relativo)
    dir_destino = path.join(dir_salida, f'PARTE{parte_actual}', dir_relativo)

    try:    
        os.makedirs(dir_destino, exist_ok=True)
    except Exception as ex:
        logger.error(f'** No se ha podido crear el directorio "{dir_destino}": {str(ex)}')
        return False
        
    try:
        os.rename(ruta_f, ruta_f_destino)
        
        comando = f'MKDIR "{dir_origen}"\n'
        if comando not in directorios_creados: 
            directorios_creados.append(comando)

        archivos_movidos.append(f'MOVE "{ruta_f_destino}" "{path.dirname(ruta_f)}"\n')
        logger.info(f'Movido "{ruta_f}" a "{ruta_f_destino}"')
    except Exception as ex:
        logger.error(f'** No se ha podido mover "{ruta_f}" a "{ruta_f_destino}": {str(ex)}')
        return False

    return True



def borrar_directorios_vacios(dname):

    if not path.exists(dname):
        return

    directorios_vacios = []

    for (dirpath, dirnames, filenames) in walk(dname, topdown=False):

        logger.info(f'Entro en directorio "{dirpath}".')

        if len(dirnames) == 0 and len(filenames) == 0:
            directorios_vacios.append(dirpath)
            logger.info(f'Está vacío.')
        else:

            for d in dirnames:
                ruta_d = path.join(dirpath, d)

                if path.exists(ruta_d):
                    logger.info(f'El directorio "{dirpath}" no está vacío.')
                    borrar_directorios_vacios(ruta_d)

                

    for d in directorios_vacios:
        try:
            if path.exists(d):
                os.rmdir(d)
                logger.info(f'Se eliminó directorio vacío "{d}".')
        except Exception as ex:
            logger.warning(f'* No se ha podido eliminar directorio vacío "{d}": {str(ex)}')



def separar(dname):
    global parte_actual
    global acum_actual
    
    # Ignorar directorio de salida
    if dname[:len(dir_salida)].lower() == dir_salida.lower():
        return

    logger.info(f'Intentando separar directorio "{dname}"...')

    # ant_dir = ''

    for (dirpath, dirnames, filenames) in walk(dname):

        # Ignorar directorio de salida
        if dirpath[:len(dir_salida)].lower() == dir_salida.lower():
            continue

        for f in filenames:

            ruta_f = path.join(dirpath, f)

            # Ignoramos archivos de la aplicación y los generados por ésta
            if ruta_f.lower() == abspath.lower() \
               or ruta_f.lower() == archivo_revertir.lower() \
               or ruta_f.lower() == archivo_log.lower():
                continue

            try:
                tamano_f = path.getsize(ruta_f)

                if tamano_f > tamano_maximo_parte:
                    logger.warning(f'* "{ruta_f}" supera el tamaño máximo permitido.')
                    continue

                acum_actual += tamano_f
            except Exception as ex:
                logger.error(f'** No se ha podido obtener tamaño del archivo "{ruta_f}": {str(ex)}')
                continue

            if acum_actual > tamano_maximo_parte:
                parte_actual += 1
                acum_actual = tamano_f

            mover(ruta_f)


if __name__ == '__main__':

    msj = 'Iniciando...'
    print(msj)
    logger.info(msj)

    if path.exists(archivo_revertir):
        try:
            os.remove(archivo_revertir)
        except Exception as ex:
            logger.error(f'** No se pudo borrar el antigüo archivo que revierte los cambios: {str(ex)}')
            exit(1)

    try:
        msj = 'Separando...'
        print(msj)
        logger.info(msj)
        separar(dir_script)

        msj = 'Borrando directorios vacíos...'
        print(msj)
        logger.info(msj)
        borrar_directorios_vacios(dir_script)
    finally:
        try:
            with open(archivo_revertir, 'w') as fi:
                fi.writelines(directorios_creados)
                fi.writelines(archivos_movidos)
        except Exception as ex:
            logger.error(f'** No se pudo generar el archivo para revertir los cambios "{archivo_revertir}"')
        
        msj = 'Fin de ejecución.'
        print(msj)
        logger.info(msj)
