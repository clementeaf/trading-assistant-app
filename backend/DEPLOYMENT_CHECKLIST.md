# Checklist de Verificación para Despliegue AWS Lambda

## ✅ Verificaciones Pre-Despliegue

### Estructura del Proyecto
- [x] Handler Lambda en `main.py` con `handler = Mangum(app, lifespan="off")`
- [x] Aplicación FastAPI en `app/main.py`
- [x] Todos los imports son relativos desde `app.`
- [x] No hay imports absolutos que dependan del sistema de archivos

### Dependencias
- [x] `requirements-lambda.txt` contiene solo dependencias de producción
- [x] No incluye dependencias de testing (pytest, etc.)
- [x] Todas las dependencias tienen versiones fijas
- [x] Mangum está incluido para compatibilidad Lambda

### Configuración
- [x] `template.yaml` está correctamente formateado
- [x] Runtime de Python es compatible (python3.11)
- [x] Variables de entorno están definidas
- [x] Handler apunta a `main.handler`
- [x] Timeout y memoria son apropiados (30s, 512MB)

### Variables de Entorno
- [x] `ECONOMIC_CALENDAR_PROVIDER` configurada
- [x] `ECONOMIC_CALENDAR_API_KEY` configurada (opcional)
- [x] `ECONOMIC_CALENDAR_API_URL` configurada
- [x] `DEFAULT_CURRENCY` configurada
- [x] `LOG_LEVEL` configurada
- [x] `STAGE` configurada

### Archivos de Configuración
- [x] `.samignore` excluye archivos innecesarios
- [x] `samconfig.toml` tiene configuración válida
- [x] `Makefile` tiene comandos útiles

### Testing
- [x] Todos los tests pasan localmente
- [x] Handler se puede importar correctamente
- [x] No hay errores de sintaxis

## 🔍 Verificaciones Post-Despliegue

### Funcionalidad
- [ ] Endpoint `/api/market-briefing/high-impact-news` responde
- [ ] Respuesta tiene formato JSON correcto
- [ ] Campo `instrument` es "XAUUSD"
- [ ] Logs en CloudWatch muestran actividad

### Performance
- [ ] Tiempo de respuesta < 5 segundos
- [ ] No hay timeouts
- [ ] Uso de memoria es razonable

### Seguridad
- [ ] API key no está expuesta en logs
- [ ] Variables de entorno están configuradas correctamente
- [ ] IAM roles tienen permisos mínimos necesarios

## 📝 Notas

- El tamaño del paquete Lambda debe ser < 50MB (sin comprimir)
- Si excede 50MB, considerar usar Lambda Layers
- Verificar límites de timeout según el proveedor de API
- Monitorear costos en CloudWatch

