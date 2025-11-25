# Sistema de Equipos Competitivos - NF1

## 🎯 Características Implementadas

### **Nueva App: competitiva**
Sistema completo de equipos y partidos team vs team para competencia organizada.

### **Modelos Creados:**

1. **Equipo**
   - Nombre y logo del equipo
   - Anfitrión (creador del equipo)
   - Descripción
   - Colores personalizables (primario y secundario)
   - Estado activo/inactivo

2. **MiembroEquipo**
   - Roles: Anfitrión, Capitán, Jugador
   - Número de camiseta
   - Estado activo

3. **PartidoCompetitivo**
   - Equipo Local vs Equipo Visitante
   - Ubicación y fecha
   - Resultados (goles)
   - Estados: Programado, En Curso, Finalizado, Cancelado
   - Creador del partido

4. **InvitacionEquipo**
   - Sistema de invitaciones con estados (Pendiente, Aceptada, Rechazada)
   - Mensaje personalizado
   - Fecha de invitación y respuesta

5. **EstadisticaJugador**
   - Goles y asistencias por partido
   - Tarjetas amarillas y rojas

### **Funcionalidades:**

#### Gestión de Equipos
- ✅ Crear equipos con nombre, logo, descripción y colores personalizados
- ✅ Ver lista de todos los equipos
- ✅ Ver detalle de equipo con miembros y partidos
- ✅ Editar equipo (solo anfitrión)
- ✅ Sistema de roles: Anfitrión, Capitán, Jugador
- ✅ Ver mis equipos
- ✅ Salir de un equipo

#### Sistema de Invitaciones
- ✅ Invitar usuarios a equipos (Anfitrión y Capitán)
- ✅ Ver invitaciones pendientes
- ✅ Aceptar o rechazar invitaciones
- ✅ Mensaje personalizado en invitaciones

#### Partidos Competitivos
- ✅ Crear partidos team vs team
- ✅ Programar fecha y ubicación
- ✅ Ver lista de partidos
- ✅ Ver detalle de partido con resultado
- ✅ Estados de partido
- ✅ Historial de partidos por equipo

### **URLs Disponibles:**
- `/competitiva/equipos/` - Lista de equipos
- `/competitiva/equipos/crear/` - Crear nuevo equipo
- `/competitiva/equipos/<id>/` - Detalle de equipo
- `/competitiva/equipos/<id>/editar/` - Editar equipo
- `/competitiva/equipos/<id>/invitar/` - Invitar miembro
- `/competitiva/equipos/<id>/salir/` - Salir del equipo
- `/competitiva/equipos/<id>/crear-partido/` - Crear partido
- `/competitiva/mis-equipos/` - Mis equipos
- `/competitiva/invitaciones/` - Mis invitaciones
- `/competitiva/partidos/` - Lista de partidos competitivos
- `/competitiva/partidos/<id>/` - Detalle de partido

### **Navbar Actualizado:**
- 🏠 Inicio
- ⚽ Partidos Friendly (antes "Partidos")
- 🛡️ Equipos (nuevo)
- 🏆 Competitivo (nuevo - partidos team vs team)
- ⭐ Ranking
- 👤 Mis Partidos

## 📋 Instalación

### 1. Ejecutar script SQL
Ejecuta el archivo `create_competitiva_tables.sql` en MySQL:

```powershell
Get-Content create_competitiva_tables.sql | mysql -u root -p nf1
```

O ejecuta manualmente en MySQL el contenido del archivo.

### 2. Crear migraciones
```powershell
.\venv\Scripts\python.exe manage.py makemigrations competitiva
.\venv\Scripts\python.exe manage.py migrate --fake
```

### 3. Crear carpeta para logos de equipos
```powershell
mkdir media\equipos
```

### 4. Iniciar servidor
```powershell
.\venv\Scripts\python.exe manage.py runserver
```

## 🎮 Cómo Usar

### Crear un Equipo:
1. Ve a "Equipos" en el navbar
2. Click en "Crear Equipo"
3. Ingresa nombre, logo (opcional), descripción
4. Selecciona colores para tu equipo
5. Automáticamente serás el Anfitrión

### Invitar Miembros:
1. Entra a tu equipo
2. Click en "Invitar Miembro"
3. Selecciona usuario y envía mensaje
4. El usuario recibirá la invitación

### Crear Partido Team vs Team:
1. Entra a tu equipo
2. Tab "Partidos" > "Crear Partido"
3. Selecciona equipo rival
4. Define ubicación y fecha
5. El partido aparecerá en "Competitivo"

## 🔥 Diferencias: Friendly vs Competitivo

### Partidos Friendly (app eventos):
- Partidos casuales donde cualquiera se puede unir
- Organizador + Participantes individuales
- +10 puntos por unirse
- +5 puntos al organizador por cada participante

### Partidos Competitivos (app competitiva):
- Partidos oficiales entre equipos organizados
- Equipo Local vs Equipo Visitante
- Requiere pertenecer a un equipo
- Estadísticas de jugadores
- Resultados y rankings de equipos

## 🎨 Características Visuales

- Colores personalizados por equipo en headers
- Logos de equipos
- Badges de roles (Anfitrión, Capitán, Jugador)
- Números de camiseta
- Estadísticas de equipos (miembros, victorias, partidos)
- Interfaz moderna con Bootstrap 5

Todo listo para competir! 🚀⚽
