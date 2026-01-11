# Code Quality - Guía y Checklist

## Objetivo

Mantener un código limpio, legible, bien documentado y con tipos correctos.

## Tools Recomendadas

### 1. Linting

**Flake8** (PEP 8 compliance):
```bash
pip install flake8
flake8 app/ tests/ --max-line-length=120 --exclude=venv,__pycache__,.pytest_cache
```

**Pylint** (más estricto):
```bash
pip install pylint
pylint app/ --max-line-length=120 --disable=C0111,C0103
```

**Configuración recomendada** (`.flake8`):
```ini
[flake8]
max-line-length = 120
exclude = venv,__pycache__,.pytest_cache,.git,migrations
ignore = E203,W503,E501
per-file-ignores =
    __init__.py:F401
```

### 2. Type Checking

**Mypy** (verificación de tipos estáticos):
```bash
pip install mypy
mypy app/ --ignore-missing-imports --no-strict-optional
```

**Configuración recomendada** (`mypy.ini`):
```ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
ignore_missing_imports = True
no_implicit_optional = True
show_error_codes = True
```

### 3. Formatting

**Black** (autoformatter opinionado):
```bash
pip install black
black app/ tests/ --line-length 120
```

**isort** (ordenar imports):
```bash
pip install isort
isort app/ tests/ --profile black --line-length 120
```

### 4. Security

**Bandit** (detección de vulnerabilidades):
```bash
pip install bandit
bandit -r app/ -ll
```

## Checklist de Code Quality

### ✅ Estilo de Código

- [ ] **PEP 8 compliance**: Código sigue convenciones de Python
- [ ] **Líneas ≤ 120 caracteres**: Legibilidad en pantallas normales
- [ ] **Imports organizados**: Stdlib → Third-party → Local (con isort)
- [ ] **Naming conventions**:
  - `snake_case` para funciones y variables
  - `PascalCase` para clases
  - `UPPER_CASE` para constantes
- [ ] **Sin código comentado** (usar git para historial)
- [ ] **Sin print statements** (usar logging)

### ✅ Type Hints

- [ ] **Funciones públicas tipadas**:
  ```python
  def calculate_correlation(prices: list[float], days: int = 30) -> float:
      ...
  ```
- [ ] **Retornos explícitos**: Todas las funciones tienen type hint de retorno
- [ ] **Tipos complejos bien anotados**:
  ```python
  from typing import Optional, Dict, List, Union
  
  def get_events(date: str) -> Optional[List[Dict[str, Union[str, float]]]]:
      ...
  ```
- [ ] **Pydantic models** para validación de datos externos

### ✅ Docstrings

- [ ] **Todas las funciones públicas documentadas** (formato Google):
  ```python
  def analyze_market(instrument: str, lookback_days: int = 30) -> MarketAnalysis:
      """
      Analiza el mercado para un instrumento dado.
      
      Args:
          instrument: Símbolo del instrumento (ej: XAUUSD)
          lookback_days: Días históricos a analizar
      
      Returns:
          MarketAnalysis: Análisis completo del mercado
      
      Raises:
          ValueError: Si el instrumento es inválido
          HTTPException: Si no se pueden obtener datos
      """
      ...
  ```
- [ ] **Clases documentadas** (qué hace, cuándo usarla)
- [ ] **Módulos documentados** (propósito del módulo)

### ✅ Error Handling

- [ ] **Try-except específicos** (no usar `except Exception:` genérico sin re-raise)
- [ ] **Logging de errores**:
  ```python
  try:
      result = risky_operation()
  except SpecificError as e:
      logger.error(f"Failed to X: {str(e)}", exc_info=True)
      raise HTTPException(status_code=500, detail="User-friendly message")
  ```
- [ ] **Validación de inputs** (Pydantic, FastAPI validators)
- [ ] **Mensajes de error útiles** (qué falló, cómo arreglarlo)

### ✅ Testing

- [ ] **Coverage ≥ 80%** en módulos críticos (services, utils)
- [ ] **Tests unitarios** para lógica de negocio
- [ ] **Tests de integración** para endpoints
- [ ] **Mocks apropiados** (no llamar APIs externas en tests)
- [ ] **Tests parametrizados** para casos múltiples:
  ```python
  @pytest.mark.parametrize("input,expected", [
      (0.5, "WEAK"),
      (0.75, "STRONG"),
      (0.9, "VERY_STRONG")
  ])
  def test_correlation_strength(input, expected):
      assert classify_strength(input) == expected
  ```

### ✅ Performance

- [ ] **Sin loops anidados innecesarios** (O(n²) → O(n) con dict lookup)
- [ ] **Lazy loading** de datos costosos
- [ ] **Async/await** en I/O operations (DB, APIs)
- [ ] **Caching** de datos que cambian poco (niveles psicológicos, configuración)
- [ ] **Batch operations** en lugar de N+1 queries

### ✅ Security

- [ ] **Sin secretos hardcodeados** (usar .env)
- [ ] **Validación de inputs** (SQL injection, XSS prevention con Pydantic)
- [ ] **Rate limiting** (en producción)
- [ ] **HTTPS only** (en producción)
- [ ] **CORS configurado** correctamente (no `allow_origins=["*"]` en prod)

### ✅ Logging

- [ ] **Logging estructurado** en producción (JSON)
- [ ] **Niveles apropiados**:
  - `DEBUG`: Detalles internos (valores intermedios)
  - `INFO`: Flujo normal (requests, operaciones exitosas)
  - `WARNING`: Situaciones anormales pero manejables
  - `ERROR`: Errores que requieren atención
  - `CRITICAL`: Sistema no funcional
- [ ] **Contexto útil** en logs:
  ```python
  logger.info(f"Processing request for {instrument}, lookback={days}")
  logger.error(f"Failed to fetch data: {error}", exc_info=True, extra={"instrument": instrument})
  ```
- [ ] **Sin información sensible** en logs (API keys, passwords)

### ✅ Code Organization

- [ ] **Single Responsibility Principle**: Cada función hace una cosa
- [ ] **DRY (Don't Repeat Yourself)**: Sin código duplicado
- [ ] **Módulos cohesivos**:
  - `models/`: Pydantic models (data structures)
  - `services/`: Business logic
  - `repositories/`: Data access layer
  - `routers/`: API endpoints (thin layer)
  - `utils/`: Helper functions (pure, stateless)
- [ ] **Dependencias explícitas** (FastAPI Depends)
- [ ] **Separación de concerns**: Lógica ≠ presentación ≠ datos

## Checklist Pre-Commit

Antes de hacer commit, verificar:

```bash
# 1. Tests pasan
pytest tests/ -v

# 2. Coverage aceptable
pytest tests/ --cov=app --cov-report=term-missing

# 3. Linting
flake8 app/ tests/

# 4. Type checking
mypy app/

# 5. Formatting
black --check app/ tests/
isort --check app/ tests/

# 6. Security
bandit -r app/ -ll
```

Si todo pasa → Hacer commit.

## Refactoring Prioritario

### Alta Prioridad

1. **Agregar type hints faltantes** en funciones públicas:
   - `app/services/*.py` (servicios principales)
   - `app/utils/*.py` (utilidades)

2. **Completar docstrings** en:
   - Todos los routers (`app/routers/market_briefing.py`)
   - Services críticos (trading_advisor, market_analysis)

3. **Mejorar error handling** en:
   - Providers (TradingEconomics, Twelve Data)
   - Services (propagar errores específicos, no genéricos)

### Media Prioridad

4. **Refactorizar funciones largas** (>50 líneas):
   - `trading_advisor_service.py::get_trading_recommendation` → Dividir en sub-métodos
   - `technical_analysis_service.py::analyze_multi_timeframe` → Extraer análisis por TF

5. **Eliminar código duplicado**:
   - Lógica de validación de instrumentos (centralizar en `validators.py`)
   - Formateo de niveles psicológicos (crear helper)

6. **Mejorar logging**:
   - Agregar logs en puntos clave de servicios
   - Estandarizar formato de mensajes

### Baja Prioridad

7. **Optimizar imports** con isort
8. **Formatear código** con black
9. **Agregar comments** solo donde la lógica no sea obvia

## Ejemplo de Refactoring

### Antes (sin tipos, sin docstring, error handling genérico):

```python
def calculate(prices, days):
    try:
        result = []
        for i in range(len(prices)):
            if i >= days:
                avg = sum(prices[i-days:i]) / days
                result.append(avg)
        return result
    except:
        return []
```

### Después (bien tipado, documentado, error handling específico):

```python
def calculate_moving_average(
    prices: list[float],
    window_days: int
) -> list[float]:
    """
    Calcula la media móvil simple (SMA) de una serie de precios.
    
    Args:
        prices: Lista de precios históricos (más reciente al final)
        window_days: Ventana de días para la media móvil
    
    Returns:
        list[float]: Lista de valores SMA (mismo length que prices, con NaN para ventana inicial)
    
    Raises:
        ValueError: Si window_days < 1 o prices está vacío
        
    Example:
        >>> prices = [100.0, 101.0, 102.0, 103.0]
        >>> calculate_moving_average(prices, window_days=2)
        [nan, 100.5, 101.5, 102.5]
    """
    if not prices:
        raise ValueError("prices list cannot be empty")
    if window_days < 1:
        raise ValueError(f"window_days must be >= 1, got {window_days}")
    
    result: list[float] = []
    for i in range(len(prices)):
        if i >= window_days:
            window = prices[i - window_days:i]
            avg = sum(window) / window_days
            result.append(avg)
        else:
            result.append(float('nan'))
    
    return result
```

## Herramientas de Integración Continua (CI)

### GitHub Actions Workflow (`.github/workflows/quality.yml`):

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install flake8 mypy black isort bandit pytest pytest-cov
      
      - name: Lint with flake8
        run: flake8 app/ tests/ --max-line-length=120
      
      - name: Type check with mypy
        run: mypy app/ --ignore-missing-imports
      
      - name: Check formatting with black
        run: black --check app/ tests/
      
      - name: Check imports with isort
        run: isort --check app/ tests/ --profile black
      
      - name: Security check with bandit
        run: bandit -r app/ -ll
      
      - name: Run tests with coverage
        run: pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
```

## Próximos Pasos

1. **Instalar herramientas**:
   ```bash
   pip install flake8 mypy black isort bandit
   ```

2. **Ejecutar checklist** en orden de prioridad

3. **Configurar pre-commit hook** (opcional):
   ```bash
   pip install pre-commit
   # Crear .pre-commit-config.yaml
   pre-commit install
   ```

4. **Iterar**: Mejorar código progresivamente, no todo de golpe

---

**Nota**: Code quality es un proceso continuo, no un estado final. El objetivo es código mantenible, no perfecto.
