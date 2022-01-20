PROPAGANDA =  '''
====================================================
GENERADOR DE COPIAS DE SEGURIDAD DE CODIGO "COPICO"
VERSION 1.0.0 (2021-07-22)
AUTOR: Marcelo Chas Cruz (chascruzrm2@gmail.com)
====================================================

'''

import subprocess
import sys, os
from datetime import datetime
import traceback

PATH_APP = "C:\\Program Files\\7-Zip"
ENTRADA_DIR = "C:\\Proyectos\\Proyecto Turnos"
SALIDA_DIR = "C:\\Proyectos\\Proyecto Turnos Backups"
NOMBRE_ARCHIVO_SALIDA = "Proyecto Turnos Updated.7z"

def generar_batch_copia():
    
    batch_copia = ''
    NOMBRE_ARCHIVO_SALIDA_COPIA = ''

    PREFIJO = datetime.now().isoformat().replace(':', '-')[:19].replace('T', '_')
    p = NOMBRE_ARCHIVO_SALIDA.rfind('.')
    
    if p >= 0:
        NOMBRE_ARCHIVO_SALIDA_COPIA = NOMBRE_ARCHIVO_SALIDA[:p] or None
        if not NOMBRE_ARCHIVO_SALIDA_COPIA:
            raise Exception('Error: El archivo de salida no tiene nombre.')
        NOMBRE_ARCHIVO_SALIDA_COPIA += f' {PREFIJO}' + NOMBRE_ARCHIVO_SALIDA[p:] # NOMBRE DE ARCHIVO MAS EXTENSION
    else:
        raise Exception('Error: El nombre de archivo de salida no tiene extensión.')

    ruta_arch_salida_copia = f'{SALIDA_DIR}\{NOMBRE_ARCHIVO_SALIDA_COPIA}'

    batch_copia = f"""
    @echo.
    @echo CREANDO COPIA AL ARCHIVO "{ruta_arch_salida_copia}"...
    COPY "{SALIDA_DIR}\{NOMBRE_ARCHIVO_SALIDA}" "{ruta_arch_salida_copia}"
    SET ERROR_APP=%ERRORLEVEL%
    @IF %ERROR_APP% NEQ 0 GOTO ERROR_COPIA
    @echo COPIA TERMINADA.
    GOTO FIN
    :ERROR_COPIA
    @echo Error en el proceso de copia de respaldo. El proceso será interrumpido. No se actualizará el archivo "{NOMBRE_ARCHIVO_SALIDA}" 1>&2
    :FIN"""

    return batch_copia


def generar_batch_compresion():
    return f"""
    PATH "{PATH_APP}"; %PATH%
    SET SALIDA_DIR={SALIDA_DIR}
    SET ENTRADA_DIR={ENTRADA_DIR}
    SET NOMBRE_ARCHIVO_SALIDA={NOMBRE_ARCHIVO_SALIDA}
    SET SALIDA_7Z="%SALIDA_DIR%\%NOMBRE_ARCHIVO_SALIDA%"

    @REM EL PARAMETRO -uq0 HACE QUE LOS ARCHIVOS BORRADOS EN EL DISCO NO SE CONSERVEN EN EL COMPRIMIDO ACTUALIZADO.

    @echo.
    @echo COMPRIMIENDO...
    7zG.exe u -t7z %SALIDA_7Z% "%ENTRADA_DIR%" -mx4 -mmt -mtm -mtc -uq0
    SET ERROR_APP=%ERRORLEVEL%
    @IF %ERROR_APP% NEQ 0 echo Error en el proceso de compresión. 1>&2
    @IF %ERROR_APP% EQU 0 explorer "%SALIDA_DIR%"
    """


def ejecutar_batch(batch, nombre_arch_temp):
    
    command = None

    if not batch:
        return False

    if not nombre_arch_temp:
        raise Exception('No se especificó nombre de archivo temporal.')

    try:
        f = open(nombre_arch_temp, 'w')
        f.write(batch)
        f.close()

        command = subprocess.run([nombre_arch_temp], capture_output=True, text=True)
        
        print(command.stdout)
        
        print('Errores:\n', command.stderr or 'No se informaron errores.')

        if not command.stderr:
            return True
    except:
        traceback.print_exc()
        print("Error: No se pudo ejecutar correctamente el proceso.")
        return False
    finally:
        print(f'Borrando archivo temporal "{nombre_arch_temp}"...')
        subprocess.run(f'cmd.exe /c DEL "{nombre_arch_temp}"')


def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    os.system('cls')
    print(PROPAGANDA)

    crear_copia = False

    while True:
        print()
        res = input(f'Quiere crear copia del archivo "{NOMBRE_ARCHIVO_SALIDA}" actual? (S/n): ').strip(' \n\r\t').upper()
        if res == 'S' or res == '':
            crear_copia = True
            break
        elif res == 'N':
            break

    fh_inicio = datetime.now()
    
    batch_copia = ''
    if crear_copia:
        batch_copia = generar_batch_copia()

    batch_compresion = generar_batch_compresion()

    res = True

    if batch_copia:
        print('CREANDO COPIA DEL ARCHIVO...')
        res = ejecutar_batch(batch_copia, 'tmp0_copia.bat')        
        
    if res:
        print('COMPRIMIENDO...')
        res = ejecutar_batch(batch_compresion, 'tmp1_compresion.bat')

    tiempo_proceso = datetime.now() - fh_inicio
    
    tiempo_amistoso = str(tiempo_proceso)
    if tiempo_amistoso.find('.') > -1:
        tiempo_amistoso = str(tiempo_proceso).split(".", 2)[0]
    
    print(f'\nProceso finalizado en {tiempo_amistoso}.\n')
    
    input('Presione ENTER para finalizar o cierre esta ventana.')

    if res: 
        sys.exit(0)
    else:
        sys.exit(-1)

main()