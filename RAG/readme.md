# Sistema de Recuperación de Documentos con RAG

Sistema de chat que responde preguntas basándose en documentos PDF utilizando RAG (Retrieval-Augmented Generation).

## Requisitos Previos

- Python 3.8+
- Ollama instalado y ejecutándose

## Instalación Rápida

1. Clona el repositorio:
```bash
git clone git@github.com:jdramosl/athenus.git
cd athenus/RAG
```

2. Crea y activa el entorno virtual:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

1. Crea un archivo `.env`:
```env
CHAT_MODEL=llama3.2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

2. Coloca tu archivo PDF en el directorio raíz (por defecto "rbf.pdf")

## Uso

1. Inicia Ollama:
```bash
ollama serve
```

2. Ejecuta la aplicación:
```bash
streamlit run app.py
```

3. Abre tu navegador en `http://localhost:8501`

## Características

- Procesamiento de documentos PDF
- Chat interactivo
- Búsqueda semántica
- Sistema de retroalimentación

## Solución de Problemas

Si encuentras errores:
1. Verifica que Ollama esté ejecutándose
2. Asegúrate de que el PDF esté en el directorio correcto
3. Revisa que todas las dependencias estén instaladas
