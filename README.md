# Sistema de Integración POS - ART MODE S.A.S. BIC

## Descripción

Sistema de integración automática para puntos de venta (POS) desarrollado para ART MODE S.A.S. BIC. Esta aplicación web permite la sincronización y automatización de datos entre diferentes sistemas de punto de venta y sistemas contables como CEGID Y2 Retail.

## Características Principales

### 🔄 Automatización de Procesos
- **Sincronización de Clientes**: Automatización de la gestión de datos de clientes
- **Interfaz Contable**: Integración automática con sistemas contables
- **Programación de Tareas**: Ejecución automática de scripts según horarios definidos
- **Modo Test**: Ambiente de pruebas para validar configuraciones

### 🌐 Aplicación Web
- **Interfaz Web Moderna**: Desarrollada con Quart (framework async de Python)
- **Panel de Control**: Gestión centralizada de todas las operaciones
- **API REST**: Endpoints para integración con sistemas externos
- **Templates Responsivos**: Interfaz adaptable a diferentes dispositivos

### 📊 Gestión de Datos
- **Clientes**: Administración completa de base de datos de clientes
- **Productos**: Gestión de catálogo de productos
- **Proveedores**: Manejo de información de proveedores
- **Tiendas**: Configuración y gestión de múltiples puntos de venta
- **Precios**: Sincronización de precios entre sistemas
- **Facturas**: Procesamiento automático de facturación

### 🏢 Integración Contable
- **CEGID Y2 Retail**: Integración nativa con el sistema contable
- **Interfaces Contables**: Generación automática de asientos contables
- **Transferencias**: Procesamiento de movimientos financieros
- **Reportes**: Generación de reportes contables automáticos

## Arquitectura del Sistema

```
src/
├── api/           # API REST endpoints
├── app/           # Aplicación web principal
├── auto/          # Scripts de automatización
├── cli/           # Interfaz de línea de comandos
├── core/          # Lógica de negocio principal
│   ├── afi/       # Interfaz contable
│   ├── bills/     # Gestión de facturas
│   ├── clients/   # Gestión de clientes
│   ├── dane/      # Integración con DANE
│   ├── products/  # Gestión de productos
│   ├── providers/ # Gestión de proveedores
│   ├── stores/    # Gestión de tiendas
│   └── prices/    # Gestión de precios
├── providers/     # Integraciones externas
├── service/       # Servicios del sistema
├── utils/         # Utilidades generales
└── web/           # Frontend web
```

## Requisitos del Sistema

### Dependencias Principales
- **Python 3.8+**
- **Quart**: Framework web asíncrono
- **Flask**: Framework web complementario
- **APScheduler**: Programación de tareas
- **Pandas**: Procesamiento de datos
- **OpenPyXL**: Manipulación de archivos Excel
- **Requests**: Cliente HTTP
- **Cryptography**: Seguridad y encriptación

### Dependencias de Desarrollo
- **PyInstaller**: Compilación de ejecutables
- **Pytest**: Testing framework
- **MyPy**: Verificación de tipos

## Instalación

### 1. Clonar el Repositorio
```bash
git clone [https://github.com/mcaro-maaji/maaji-integracion-pos.git]
cd "Integracion - POS"
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear archivo `.env` basado en el ejemplo proporcionado:
```bash
cp .env.example .env
```

### 5. Preparar Datos
Asegurar que los archivos de configuración estén en la carpeta `data/`:
- `Tiendas_CEGID_Y2_Retail.xlsx`
- `Proveedores_CEGID_Y2_Retail.xlsx`
- `Interfaz_Contable_Parametros_CEGID_Y2_Retail.xlsx`
- `Dane_Municipios.xlsx`

## Uso

### Ejecutar la Aplicación

#### Modo Desarrollo
```bash
cd src/
python -m main
```

#### Modo Producción con Automatización
```bash
cd src/
python -m main --auto
```

#### Modo Test
```bash
cd src/
python -m main --auto --auto-test
```

### Compilar Ejecutable
```bash
pyinstaller integracion-pos.spec
```

El ejecutable se generará en la carpeta `dist/`.

## Configuración

### Archivo de Configuración Principal
El sistema utiliza archivos JSON para la configuración de automatización:
- `static/data/auto/clientes.automatizacionpos.json`
- `static/data/auto/interfaz_contable.automatizacionpos.json`
- `static/data/auto/test.clientes.automatizacionpos.json`
- `static/data/auto/test.interfaz_contable.automatizacionpos.json`

### Variables de Entorno
Configurar las siguientes variables en el archivo `.env`:
- Credenciales de base de datos
- Configuraciones de conexión
- Parámetros de seguridad

## API Endpoints

La aplicación expone una API REST para integración externa e.j.:

- `GET /api/clients` - Obtener lista de clientes
- `POST /api/clients` - Crear nuevo cliente
- `GET /api/products` - Obtener catálogo de productos
- `POST /api/sync` - Ejecutar sincronización manual
- `GET /api/status` - Estado del sistema

## Testing [No Implementados :p]

### Ejecutar Pruebas
```bash
pytest src/test/
```

### Ejecutar Pruebas con Cobertura
```bash
pytest src/test/ --cov=src/
```

## Estructura de Logs

El sistema mantiene logs detallados en:
- Logs de aplicación web
- Logs de automatización
- Logs de integración contable
- Logs de errores y excepciones

## Seguridad

- **Encriptación**: Credenciales encriptadas con clave salt
- **Autenticación**: Sistema de login seguro
- **Validación**: Validación de datos en todas las operaciones
- **Logs de Auditoría**: Registro de todas las operaciones críticas

## Desarrollo

### Estructura del Proyecto
- **Separación de Responsabilidades**: Cada módulo tiene una función específica
- **Arquitectura Modular**: Fácil mantenimiento y extensión
- **Programación Asíncrona**: Uso de async/await para mejor rendimiento
- **Patrones de Diseño**: Implementación de mejores prácticas

### Contribuir
1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

**Manuel Caro** - *ART MODE S.A.S. BIC*

## Soporte Técnico

Para soporte técnico o consultas sobre la implementación, contactar al equipo de desarrollo de ART MODE S.A.S. BIC.

---

*Sistema desarrollado específicamente para las necesidades de integración POS de ART MODE S.A.S. BIC*
