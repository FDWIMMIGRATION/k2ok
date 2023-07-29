""""
Instrucciones
Se tiene los archivos de ejemplo para mostrar una aplicación docker con python.

Empaquetar aplicación

docker build -t app-flask .

Ejecutar contenedor docker run -it -p 5000:5000 app-flask

Multi-stage builds
# Primera imagen para compilar 
FROM python:3.10.11-slim-buster as compile-image
# Se define una variable opcional
RUN python3 -m venv /opt/venv
# Se sobreescribe la variable path para que tenga prioridad los comandos del ambiente
ENV PATH="/opt/venv/bin:$PATH"
# Se copia unicamente el archivo de dependencias 
COPY requirements.txt /requirements.txt
# Se instalan las dependencias.
RUN pip install -r requirements.txt
# Listo, inicia el segundo contenedor 
FROM python:3.8.4-alpine3.12 AS build-image
# Se copia la carpeta venv que contiene todas las dependencias en el segundo contenedor
COPY --from=compile-image /opt/venv /opt/venv
# Se copia la aplicación
COPY . usr/src/app
# Se establece por defecto el directorio 
WORKDIR /usr/src/app
# Se agrega el directorio a las variables de ambiente.
ENV PATH="/opt/venv/bin:$PATH"
# Arranca la aplicación
ENTRYPOINT python3 main.py

#activar entorno virtul
./venv/Scripts/activate 

# desactivar entorno virtual
deactivate

#actualizar las librerias requirements.txt
pip install -r requirements.txt --upgrade

# actualizar los datos agregandole version
pip freeze > requirements.txt

cls

# crear imagen de contenedor
docker build -t fdwaplic .

docker ps -a # Muestra todos los contenedores (incluso los que no están en ejecución)
docker images -a # Muestra todas las imágenes (incluso las que no están etiquetadas)

#detener y elimar contenedores
docker-compose down

#crear imagen
docker-compose up --build

docker images
#renombrar imagen docker
docker image tag appfw cabreram/fdw: escribe el nombre ede etiqueta
#subir imagen docker
docker push cabreram/fdw: escribe el nombre ede etiqueta
""""
#detener contenedor
docker stop $(docker ps -q)
#eliminar contenedores detenidos
docker rm $(docker ps -a -q)
#eliminar solo contenedores detenidos
docker rm -v $(docker ps -a -q)
