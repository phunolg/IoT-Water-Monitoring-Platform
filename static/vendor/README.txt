/* Vendor Library Information */

/*
This vendor directory contains third-party libraries used in the Smart Water Monitoring System:

1. chart.min.js (v4.4.0)
   - Chart.js library for interactive data visualization
   - Used for pH, TDS, NTU charts and real-time data plotting
   - Documentation: https://www.chartjs.org/

2. bootstrap.min.css (v5.3.2)
   - Bootstrap CSS framework for responsive design
   - Provides grid system, components, and utilities
   - Documentation: https://getbootstrap.com/

3. bootstrap.min.js (v5.3.2)
   - Bootstrap JavaScript for interactive components
   - Includes modals, dropdowns, tooltips, etc.
   - Bundled with Popper.js for positioning

Usage in templates:
{% load static %}
<link rel="stylesheet" href="{% static 'vendor/bootstrap.min.css' %}">
<script src="{% static 'vendor/bootstrap.min.js' %}"></script>
<script src="{% static 'vendor/chart.min.js' %}"></script>
*/