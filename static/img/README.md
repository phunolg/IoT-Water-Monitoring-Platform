# Static Images Directory

This directory contains icons and graphics for the Smart Water Monitoring System dashboard:

## Icons
- **logo.svg** - Main application logo with water drop design
- **ph-icon.svg** - pH level indicator icon (blue theme)
- **tds-icon.svg** - TDS (Total Dissolved Solids) icon (green theme)  
- **ntu-icon.svg** - NTU (Turbidity) icon (orange theme)
- **esp32-icon.svg** - ESP32 device status icon

## Usage in Templates
```html
{% load static %}
<img src="{% static 'img/logo.svg' %}" alt="Smart Water Monitoring" width="100">
<img src="{% static 'img/ph-icon.svg' %}" alt="pH Level" width="60">
<img src="{% static 'img/tds-icon.svg' %}" alt="TDS Level" width="60">
<img src="{% static 'img/ntu-icon.svg' %}" alt="NTU Level" width="60">
<img src="{% static 'img/esp32-icon.svg' %}" alt="ESP32 Device" width="80">
```

## Design Guidelines
- Icons use consistent color scheme matching dashboard theme
- SVG format for crisp display at any size
- Transparent backgrounds for flexible placement
- Icons sized at 60x60px for dashboard cards
- Logo sized at 100x100px for headers

## Color Palette
- **Primary Blue**: #2196F3 (pH, Logo)
- **Success Green**: #4CAF50 (TDS)
- **Warning Orange**: #FF9800 (NTU)
- **Dark Gray**: #333 (ESP32, Text)