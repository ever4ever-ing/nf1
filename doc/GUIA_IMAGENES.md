# Guía de Uso de Imágenes y Estilos

## 📁 Estructura Creada

```
eventos/
└── static/
    └── eventos/
        ├── css/
        │   └── styles.css          # Estilos personalizados
        └── img/
            ├── field-pattern.svg    # Patrón de cancha (ejemplo)
            └── README.md            # Guía de imágenes
```

## 🎨 Archivo CSS Creado

El archivo `styles.css` incluye:

### Clases Disponibles

1. **Hero Section**
   ```html
   <div class="hero-section">
       <h1>Tu contenido aquí</h1>
   </div>
   ```

2. **Backgrounds con Gradientes**
   ```html
   <div class="gradient-primary">Fondo morado</div>
   <div class="gradient-success">Fondo verde</div>
   <div class="gradient-info">Fondo azul</div>
   ```

3. **Cards con Hover Effect**
   ```html
   <div class="card partido-card">
       <!-- Contenido -->
   </div>
   ```

4. **Contenedor de Imágenes con Zoom**
   ```html
   <div class="img-container">
       <img src="..." alt="...">
   </div>
   ```

5. **Overlay Oscuro para Fondos**
   ```html
   <div class="bg-soccer overlay-dark">
       <p>Texto sobre fondo oscuro</p>
   </div>
   ```

6. **Animación Fade In**
   ```html
   <div class="fade-in">
       <!-- Se anima al cargar -->
   </div>
   ```

## 🖼️ Cómo Agregar Imágenes

### 1. Agregar imagen al proyecto

Coloca tus imágenes en: `eventos/static/eventos/img/`

### 2. Usar en templates

```html
{% load static %}
<img src="{% static 'eventos/img/tu-imagen.jpg' %}" alt="Descripción">
```

### 3. Background en CSS

```css
.mi-seccion {
    background-image: url('{% static "eventos/img/background.jpg" %}');
}
```

### 4. Inline style

```html
{% load static %}
<div style="background-image: url('{% static 'eventos/img/hero.jpg' %}');">
    Contenido
</div>
```

## 📝 Ejemplos de Uso

### Hero con Background

```html
{% load static %}
<section class="hero-section" style="background-image: url('{% static 'eventos/img/field-bg.jpg' %}'); background-size: cover;">
    <div class="overlay-dark">
        <h1>Bienvenido a NF1 Eventos</h1>
        <p>Conecta con jugadores</p>
    </div>
</section>
```

### Card con Imagen

```html
{% load static %}
<div class="card partido-card">
    <img src="{% static 'eventos/img/soccer.jpg' %}" class="card-img-top" alt="Fútbol">
    <div class="card-body">
        <h5 class="card-title">Partido del Sábado</h5>
    </div>
</div>
```

## 🌐 Recursos Gratuitos Recomendados

### Imágenes
- **Unsplash**: https://unsplash.com/s/photos/soccer
- **Pexels**: https://www.pexels.com/search/football/
- **Pixabay**: https://pixabay.com/images/search/soccer/

### Iconos
- **Flaticon**: https://www.flaticon.com/
- **Font Awesome**: https://fontawesome.com/
- **Bootstrap Icons**: https://icons.getbootstrap.com/

### Herramientas
- **TinyPNG**: https://tinypng.com/ (comprimir imágenes)
- **Remove.bg**: https://www.remove.bg/ (quitar fondos)
- **Canva**: https://www.canva.com/ (crear diseños)

## 💡 Consejos

1. **Optimiza las imágenes** antes de subirlas (< 500KB)
2. **Usa formatos modernos** (WebP) cuando sea posible
3. **Nombres descriptivos**: `hero-background.jpg` mejor que `img1.jpg`
4. **Alt text** siempre para accesibilidad
5. **Lazy loading** para imágenes grandes:
   ```html
   <img src="..." loading="lazy" alt="...">
   ```

## 🚀 Próximos Pasos

1. Descarga imágenes de fútbol/canchas de los sitios recomendados
2. Colócalas en `eventos/static/eventos/img/`
3. Actualiza los templates para usarlas
4. Ejecuta `python manage.py collectstatic` en producción
