liturgy_converter_app/
├── main.py                 # Punto de entrada principal
├── ui/                     # Módulos de interfaz
│   ├── __init__.py
│   ├── dashboard.py        # Pantalla principal
│   ├── import_module.py    # Módulo de importación
│   ├── editor.py          # Editor avanzado
│   ├── content_manager.py # Gestor de contenido
│   └── admin.py           # Administración
├── core/                   # Lógica de negocio
│   ├── __init__.py
│   ├── database.py        # Conexión MySQL
│   ├── file_processor.py  # Procesamiento archivos
│   ├── ocr_engine.py      # Procesamiento OCR
│   └── web_scraper.py     # Web scraping
├── utils/                  # Utilidades
│   ├── __init__.py
│   ├── validators.py      # Validación datos
│   └── helpers.py         # Funciones auxiliares
└── assets/                # Recursos
    ├── icons/
    └── styles/