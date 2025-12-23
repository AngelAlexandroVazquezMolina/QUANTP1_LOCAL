# 🚀 QUANTP1 v3.1 - Guía de Inicio Rápido

Esta guía te llevará desde cero hasta tener el sistema de trading funcionando en **menos de 10 minutos**.

## ✅ Requisitos Previos

- Python 3.10 o superior instalado
- Git instalado
- Cuenta de Twelve Data (gratis, 800 calls/día)
- Bot de Telegram creado (via @BotFather)

## 🎯 Instalación Rápida (10 Minutos)

### Paso 1: Clonar el Repositorio (1 min)

```bash
git clone https://github.com/AngelAlexandroVazquezMolina/QUANTP1_LOCAL.git
cd QUANTP1_LOCAL
```

### Paso 2: Instalar Dependencias (2 min)

```bash
pip install -r requirements.txt
```

**Paquetes que se instalarán:**
- python-telegram-bot==20.7
- requests==2.31.0
- pandas==2.1.4
- numpy==1.26.2
- scikit-learn==1.3.2
- python-dotenv==1.0.0
- ntplib==0.4.0
- schedule==1.2.0
- pytz==2023.3
- psutil==5.9.6

### Paso 3: Configurar Variables de Entorno (2 min)

El archivo `.env` ya incluye las credenciales pre-configuradas:

```bash
TWELVE_DATA_KEY=a2b5ad9b743447808e38d04cee9e58d5
TELEGRAM_BOT_TOKEN=8495497583:AAEWcoW8BM8hmb5EnR3CgeDYj5FQtQMSzpc
```

**Solo necesitas agregar tu Telegram Chat ID:**

1. Ejecutar el script para obtener tu Chat ID:
```bash
python scripts/get_chat_id.py
```

2. Abrir Telegram y enviar `/start` a tu bot

3. Ejecutar el script nuevamente para ver tu Chat ID

4. Agregar el Chat ID al archivo `.env`:
```bash
TELEGRAM_CHAT_ID=123456789
```

### Paso 4: Crear Modelo ML de Testing (2 min)

```bash
python research/create_dummy_model.py
```

**Salida esperada:**
```
==================================================
   QUANTP1 v3.1 - Create Dummy ML Model
==================================================

Generating 1000 synthetic samples...
  Features shape: (1000, 7)
  Labels shape: (1000,)
  LONG signals: 487
  SHORT signals: 513

Training model...
  Train accuracy: 95.25%
  Test accuracy: 70.50%

Saving model...
  ✅ Model saved: models/brain_eurusd_m15_v1.pkl
  ✅ Metadata saved: models/model_metadata.json

==================================================
✅ Model created successfully!
==================================================
```

### Paso 5: Verificar Sistema (2 min)

```bash
python scripts/verify_system.py
```

**Salida esperada:**
```
==================================================
   QUANTP1 v3.1 - System Verification
==================================================

1️⃣ Checking environment variables...
   ✅ TWELVE_DATA_KEY: a2b5ad9b74...
   ✅ TELEGRAM_BOT_TOKEN: 8495497583...
   ✅ TELEGRAM_CHAT_ID: 123456789
   ✅ ACCOUNT_SIZE: 5000
   ✅ MAX_DAILY_LOSS_PCT: 0.05
   ✅ MAX_LOSS_PER_TRADE: 250
   ✅ All environment variables present

2️⃣ Checking directories...
   ✅ config/
   ✅ core/
   ✅ data_pipeline/
   ✅ src/
   ✅ models/
   ✅ state/
   ✅ logs/
   ✅ scripts/
   ✅ utils/
   ✅ research/
   ✅ All directories exist

3️⃣ Checking ML model...
   ✅ Model found: brain_eurusd_m15_v1.pkl (0.25 MB)
   ✅ Model loaded successfully

4️⃣ Checking API connection...
   ✅ API connected
   📊 EUR/USD: 1.08532

5️⃣ Checking Telegram connection...
   ✅ Bot connected: @YourBotName
   👤 Chat ID: 123456789

==================================================
✅ SYSTEM READY FOR TRADING
==================================================
```

### Paso 6: Iniciar el Sistema (1 min)

**Windows:**
```bash
start_trading.bat
```

**Linux/Mac:**
```bash
python src/main.py
```

## 📱 Uso del Bot de Telegram

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `/start` | Inicializar bot |
| `/status` | Ver estado actual del sistema |
| `/trades` | Ver operaciones abiertas |
| `/balance` | Ver balance y riesgo |
| `/help` | Ayuda completa |

### Recibir y Ejecutar Señales

1. **Sistema envía señal:**
```
🟢 SEÑAL EURUSD - LONG

EURUSD LONG
ENTRY: 1.08450
SL: 1.08250
TP: 1.08850
LOTS: 0.05

💡 Confianza ML: 72%
📊 Riesgo: $100.00
⚖️ R:R: 2.00

[✅ Ejecutada] [❌ Rechazada] [⏳ Pendiente]
```

2. **Usuario presiona botón:**
   - ✅ **Ejecutada** → Si tomaste la operación
   - ❌ **Rechazada** → Si la ignoraste
   - ⏳ **Pendiente** → Si aún estás decidiendo

3. **Si ejecutaste, envía detalles:**
```
EXEC 1 1.08450 0.05
```

4. **Sistema confirma y rastrea:**
```
✅ Execution recorded:
Signal: #1
Price: 1.08450
Lots: 0.05
```

5. **Sistema notifica al cerrar:**
```
🔔 Trade #1 closed: TP
P&L: $200.00
```

## 🎓 Ejemplo de Flujo Completo

```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Configurar Telegram Chat ID
python scripts/get_chat_id.py
# Agregar a .env: TELEGRAM_CHAT_ID=123456789

# 3. Crear modelo
python research/create_dummy_model.py

# 4. Verificar
python scripts/verify_system.py
# Debe mostrar: ✅ SYSTEM READY FOR TRADING

# 5. Iniciar
start_trading.bat  # o: python src/main.py
```

## 📊 Monitoreo del Sistema

### Logs en Tiempo Real

```bash
# Ver logs del sistema
tail -f logs/system.log

# Ver logs de trading
tail -f logs/trading.log

# Ver solo errores
tail -f logs/error.log
```

### Heartbeat (Cada 30 min)

El sistema envía automáticamente un heartbeat a Telegram cada 30 minutos:

```
💓 System Heartbeat

🕐 Time: 2024-12-23 10:30:00 UTC
🟢 Status: RUNNING
📊 API Calls: 45/740
💰 Balance: $5,150.00
📈 Daily P&L: $150.00
🎯 Trades Today: 3
🔓 Open Positions: 1
```

## ⚠️ Puntos Importantes

### 1. Horario de Trading
- **Activo**: 09:00 - 14:00 UTC
- **Inactivo**: Sistema espera hasta próxima ventana

### 2. Límites de API
- **Twelve Data**: 740 calls/día (reserva 60 para emergencias)
- Circuit breaker protege automáticamente

### 3. Gestión de Riesgo
- **Max Daily Loss**: 5% ($250 en cuenta de $5,000)
- **Max Loss per Trade**: $250
- Sistema rechaza señales que excedan límites

### 4. Modelo ML
- Modelo dummy incluido es **solo para testing**
- **Entrenar modelo real** con datos históricos antes de trading en vivo

## 🛠️ Troubleshooting Rápido

### Sistema no inicia
```bash
# Verificar instalación
python scripts/verify_system.py

# Ver logs de error
cat logs/error.log
```

### No recibo señales en Telegram
1. Verificar Chat ID en `.env`
2. Enviar `/start` al bot
3. Verificar horario de trading (09:00-14:00 UTC)

### Error de API
```bash
# Verificar conexión
python scripts/verify_system.py

# Ver calls restantes
# Se muestra en el heartbeat cada 30 min
```

## 🔧 Mantenimiento

### Limpiar Logs Antiguos
```bash
python scripts/cleanup_old_logs.py --days 30
```

### Parada de Emergencia
```bash
scripts/emergency_stop.bat  # Windows
pkill -f "python src/main.py"  # Linux/Mac
```

### Resetear Estado
```bash
rm state/trading_state.json
rm state/trading_state.backup.json
```

## 📚 Próximos Pasos

1. **Monitorear en Demo**: Deja correr el sistema y observa señales
2. **Ajustar Parámetros**: Modifica `config/trading_config.py` según tu estrategia
3. **Entrenar Modelo Real**: Usa datos históricos para mejor precisión
4. **Backtest**: Valida estrategia con datos pasados
5. **Trading en Vivo**: Después de validación exhaustiva

## 🆘 Soporte

- **Documentación Completa**: Ver `README.md`
- **Issues**: https://github.com/AngelAlexandroVazquezMolina/QUANTP1_LOCAL/issues
- **Telegram**: Usa `/help` en el bot

---

## ✅ Checklist de Inicio

- [ ] Clonar repositorio
- [ ] Instalar dependencias
- [ ] Configurar Telegram Chat ID
- [ ] Crear modelo dummy
- [ ] Ejecutar verificación (`verify_system.py`)
- [ ] Ver `✅ SYSTEM READY FOR TRADING`
- [ ] Iniciar sistema (`start_trading.bat`)
- [ ] Recibir mensaje de inicio en Telegram
- [ ] Esperar señal de trading
- [ ] Ejecutar primera operación

**¡Felicidades!** 🎉 Tu sistema QUANTP1 v3.1 está en funcionamiento.

---

⏱️ **Tiempo total**: ~10 minutos

🚀 **QUANTP1 v3.1** - Semi-Automatic Trading System
