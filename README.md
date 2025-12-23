# QUANTP1 v3.1 - Sistema de Trading Semi-Automático

Sistema completo de trading algorítmico para EURUSD M15 con estrategia Mean Reversion + Machine Learning.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)

## 🎯 Características Principales

- **Estrategia Híbrida**: Mean Reversion + Machine Learning (RandomForest)
- **Bot de Telegram Interactivo**: Señales con botones para confirmar ejecución
- **Gestión de Riesgo Prop Firm**: Límites 5% diario, $250 por operación
- **Circuit Breaker API**: Protección límite 740 calls/día (Twelve Data)
- **Anti-Repainting**: Solo velas cerradas en análisis
- **Persistencia Atómica**: Guardado seguro de estado con backups
- **Sincronización NTP**: Tiempo preciso sin permisos admin
- **Health Monitoring**: CPU, RAM, disco, red

## 📊 Stack Tecnológico

- **Python 3.10+**
- **Twelve Data API** - Datos de mercado en tiempo real
- **Telegram Bot API** - Notificaciones interactivas
- **scikit-learn** - Modelo de Machine Learning
- **pandas/numpy** - Procesamiento de datos
- **ntplib** - Sincronización de tiempo

## 🏗️ Arquitectura del Sistema

```
QUANTP1_LOCAL/
├── config/              # Configuración modular (API, trading, risk, ML)
├── core/                # Sistema central (state, circuit breaker, time sync)
├── data_pipeline/       # Pipeline de datos (API client, validación)
├── src/
│   ├── strategy/        # Indicadores y generación de señales
│   ├── ml/              # Modelo ML y predicciones
│   ├── risk/            # Gestión de riesgo y validación
│   ├── notifications/   # Bot Telegram y alertas
│   └── main.py         # ⭐ Orquestador principal
├── scripts/            # Utilidades (verificación, chat ID, limpieza)
├── research/           # Laboratorio (crear modelo dummy)
├── models/             # Modelos ML (.pkl files)
├── state/              # Estado persistente (JSON)
├── logs/               # Logs con rotación automática
└── utils/              # Logger y time utilities
```

## 📦 Instalación

### 1. Clonar Repositorio

```bash
git clone https://github.com/AngelAlexandroVazquezMolina/QUANTP1_LOCAL.git
cd QUANTP1_LOCAL
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

El archivo `.env` ya incluye las credenciales pre-configuradas. Solo necesitas agregar tu `TELEGRAM_CHAT_ID`:

```bash
# Obtener Chat ID
python scripts/get_chat_id.py

# Agregar a .env
TELEGRAM_CHAT_ID=123456789
```

### 4. Crear Modelo ML (Dummy para Testing)

```bash
python research/create_dummy_model.py
```

### 5. Verificar Sistema

```bash
python scripts/verify_system.py
```

Debe mostrar: `✅ SYSTEM READY FOR TRADING`

## 🚀 Uso

### Inicio del Sistema

**Windows:**
```bash
start_trading.bat
```

**Linux/Mac:**
```bash
python src/main.py
```

### Comandos del Bot de Telegram

- `/start` - Inicializar bot
- `/status` - Estado actual del sistema
- `/trades` - Ver operaciones abiertas
- `/balance` - Balance y riesgo disponible
- `/help` - Ayuda y comandos

### Workflow de Señales

1. **Sistema genera señal** → Envía a Telegram con botones
2. **Usuario revisa** → Presiona ✅ Ejecutada / ❌ Rechazada / ⏳ Pendiente
3. **Usuario ejecuta** → Envía: `EXEC <signal_id> <precio> <lotes>`
4. **Sistema rastrea** → Actualiza P&L, detecta SL/TP
5. **Sistema notifica** → Al cerrar posición

## 📈 Estrategia de Trading

### Indicadores Técnicos

- **Z-Score** (20 periodos) - Mean reversion
- **ADX** (14 periodos) - Fuerza de tendencia
- **RSI** (14 periodos) - Sobrecompra/sobreventa
- **Bollinger Bands** (20, 2.0) - Volatilidad

### Reglas de Señales

**LONG:**
- Z-Score ≤ -2.0 (precio bajo vs media)
- ADX < 30 (sin tendencia fuerte)
- RSI < 40 (sobreventa)
- ML Confidence ≥ 65%

**SHORT:**
- Z-Score ≥ 2.0 (precio alto vs media)
- ADX < 30 (sin tendencia fuerte)
- RSI > 60 (sobrecompra)
- ML Confidence ≥ 65%

### Gestión de Riesgo

- **Max Daily Loss**: 5% del capital ($250 en cuenta de $5,000)
- **Max Loss per Trade**: $250
- **Default Risk per Trade**: 2% del capital
- **Max Open Positions**: 3
- **Max Daily Trades**: 10
- **Risk/Reward Ratio**: Mínimo 1.5:1

## ⚙️ Configuración

### Trading Parameters (`config/trading_config.py`)

```python
SYMBOL = "EUR/USD"
TIMEFRAME = "15min"
TRADING_START_HOUR = 9   # 09:00 UTC
TRADING_END_HOUR = 14    # 14:00 UTC
```

### Risk Parameters (`config/risk_config.py`)

```python
ACCOUNT_SIZE = 5000
MAX_DAILY_LOSS_PCT = 0.05  # 5%
MAX_LOSS_PER_TRADE = 250   # $250
```

### ML Configuration (`config/ml_config.py`)

```python
MIN_CONFIDENCE_THRESHOLD = 0.65  # 65%
MAX_MODEL_AGE_DAYS = 90
```

## 🛠️ Utilidades

### Verificar Sistema
```bash
python scripts/verify_system.py
```

### Obtener Telegram Chat ID
```bash
python scripts/get_chat_id.py
```

### Limpiar Logs Antiguos
```bash
python scripts/cleanup_old_logs.py --days 30
```

### Parada de Emergencia
```bash
scripts/emergency_stop.bat  # Windows
pkill -f "python src/main.py"  # Linux/Mac
```

## 📝 Logs

Los logs se guardan en `logs/` con rotación automática:

- **system.log** - Log general del sistema (rotación diaria, 30 días)
- **trading.log** - Todas las operaciones (rotación diaria, 30 días)
- **error.log** - Solo errores (rotación por tamaño, 10MB)

## 🔒 Seguridad

- ✅ `.env` excluido de Git
- ✅ State files y modelos excluidos de Git
- ✅ Circuit breaker para proteger API
- ✅ Validación de riesgo antes de cada señal
- ✅ Atomic state saves con fsync()
- ✅ Backup automático de estado

## 🐛 Troubleshooting

### Error: "Model not found"
```bash
python research/create_dummy_model.py
```

### Error: "API connection failed"
- Verificar `TWELVE_DATA_KEY` en `.env`
- Comprobar límite de calls diarios (800/día)

### Error: "Telegram connection failed"
- Verificar `TELEGRAM_BOT_TOKEN` en `.env`
- Obtener `TELEGRAM_CHAT_ID`: `python scripts/get_chat_id.py`

### Error: "NTP sync failed"
- No crítico, usa hora del sistema
- Verificar firewall permite UDP 123

## ⚠️ Disclaimer

**IMPORTANTE**: Este sistema es para fines educativos y de investigación. El trading conlleva riesgos significativos. Prueba en cuenta demo antes de usar con dinero real.

- ❌ NO ejecuta operaciones automáticamente (semi-automático)
- ⚠️ Usuario debe confirmar cada señal manualmente
- 📊 Modelo ML dummy incluido solo para testing
- 🎓 Entrena modelo real con datos históricos antes de trading en vivo

## 📚 Recursos

- **Twelve Data API**: https://twelvedata.com/
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **scikit-learn**: https://scikit-learn.org/

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Angel Alejandro Vazquez Molina**

- GitHub: [@AngelAlexandroVazquezMolina](https://github.com/AngelAlexandroVazquezMolina)

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!

**QUANTP1 v3.1** - Semi-Automatic Trading System | 2024
