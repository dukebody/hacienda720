Utilidades para generar un archivo 720 para importar en la herramienta de Hacienda.

Ahora mismo sólo hay un módulo para leer la hoja de balance de Mintos. Idealmente se puede extender fácilmente a otras plataformas, ya sea crowd o bolsa.

Instrucciones de uso:

- Cambiar las variables en mayúsculas de arriba del archivo `mintos.py` con los datos propios. Se espera que los archivos de entrada estén en el mismo directorio del script.
- A tener en cuenta al exportar el archivo CSV:
  - Asegurarse que las cantidades tengas todos los decimales (suelen ser 6). Excel puede redondear a 2 al exportar sin darnos cuenta.
  - Asegurarse el formato de las cantidades. Solo se soporta español (12.345,67), ingles (12,345.67) o estandar (12345.67).
- Ejecutar `python mintos.py`. Generará un archivo con el nombre `OUTPUT_FILENAME`, que se puede importar en la herramienta web de Hacienda.
