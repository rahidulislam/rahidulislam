## templates/base/base.html
```
<!DOCTYPE html>
{% load static %}
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta content="width=device-width, initial-scale=1.0" name="viewport">

  <title>{% block title %}{% endblock title %}</title>
  <meta content="" name="description">
  <meta content="" name="keywords">

  <!-- Favicons -->

  <link rel="apple-touch-icon" sizes="180x180" href="{% static 'img/apple-touch-icon.png' %}">
  <link rel="icon" type="image/png" sizes="32x32" href="{% static 'img/favicon-32x32.png' %}">
  <link rel="icon" type="image/png" sizes="16x16" href="{% static 'img/favicon-16x16.png' %}">
  <link rel="manifest" href="{% static 'img/site.webmanifest' %}">

  <!-- Google Fonts -->
  <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,300i,400,400i,600,600i,700,700i|Raleway:300,300i,400,400i,500,500i,600,600i,700,700i|Poppins:300,300i,400,400i,500,500i,600,600i,700,700i" rel="stylesheet">

  {% include 'base/style.html' %}

  <!-- =======================================================
  * Template Name: Personal
  * Updated: Aug 30 2023 with Bootstrap v5.3.1
  * Template URL: https://bootstrapmade.com/personal-free-resume-bootstrap-template/
  * Author: BootstrapMade.com
  * License: https://bootstrapmade.com/license/
  ======================================================== -->
  <!-- Custom Design Template -->
</head>

<body>
  {% include 'base/messages.html' %}
  
  {% include 'layout/header.html' %}

  {% block content %}{% endblock content %}

  {% include 'layout/footer.html' %}

  {% include 'base/script.html' %}

</body>

</html>
```

## templates/base/base_project.html
```
<!DOCTYPE html>
{% load static %}
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta content="width=device-width, initial-scale=1.0" name="viewport">

  <title>{% block title %}{% endblock title %}</title>
  <meta content="" name="description">
  <meta content="" name="keywords">

  <!-- Favicons -->
  <link rel="apple-touch-icon" sizes="180x180" href="{% static 'img/apple-touch-icon.png' %}">
  <link rel="icon" type="image/png" sizes="32x32" href="{% static 'img/favicon-32x32.png' %}">
  <link rel="icon" type="image/png" sizes="16x16" href="{% static 'img/favicon-16x16.png' %}">
  <link rel="manifest" href="{% static 'img/site.webmanifest' %}">

  <!-- Google Fonts -->
  <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,300i,400,400i,600,600i,700,700i|Raleway:300,300i,400,400i,500,500i,600,600i,700,700i|Poppins:300,300i,400,400i,500,500i,600,600i,700,700i" rel="stylesheet">

  {% include 'base/style.html' %}
  
  <!-- =======================================================
  * Template Name: Personal
  * Updated: Aug 30 2023 with Bootstrap v5.3.1
  * Template URL: https://bootstrapmade.com/personal-free-resume-bootstrap-template/
  * Author: BootstrapMade.com
  * License: https://bootstrapmade.com/license/
  ======================================================== -->
  <!-- Custom Design Template -->
</head>

<body>
  

  <main id="main">
    {% include 'base/messages.html' %}

    {% block content %}{% endblock content %}
    
  </main><!-- End #main -->

  {% include 'layout/footer.html' %}

  {% include 'base/script.html' %}
</body>

</html>
```

## templates/layout/header.html
```
  <!-- ======= Header ======= -->
  <header id="header">
    <div class="container">

      <h1><a href="{% url 'home:home' %}">{{personal_info.name}}</a></h1>
      <!-- Uncomment below if you prefer to use an image logo -->
      <!-- <a href="index.html" class="mr-auto"><img src="assets/img/logo.png" alt="" class="img-fluid"></a> -->
      <h2>I'm a passionate <span>{{personal_info.profession}}</span> from Bangladesh</h2>

      <nav id="navbar" class="navbar">
        <ul>
          <li><a class="nav-link active" href="#header">Home</a></li>
          <li><a class="nav-link" href="#about">About</a></li>
          <li><a class="nav-link" href="#resume">Resume</a></li>
          <li><a class="nav-link" href="#services">Services</a></li>
          <li><a class="nav-link" href="#portfolio">Portfolio</a></li>
          <li><a class="nav-link" href="#contact">Contact</a></li>
        </ul>
        <i class="bi bi-list mobile-nav-toggle"></i>
      </nav><!-- .navbar -->

      <div class="social-links">
        
        {% for social_item in social_items %}
          <a href="{{social_item.social_link}}" class="twitter"><i class="bi bi-{{social_item.name}}"></i></a>
        {% endfor %}
          
      </div>

    </div>
  </header><!-- End Header -->
```

## templates/layout/footer.html
```
<div class="credits">
    <!-- All the links in the footer should remain intact. -->
    <!-- You can delete the links only if you purchased the pro version. -->
    <!-- Licensing information: https://bootstrapmade.com/license/ -->
    <!-- Purchase the pro version with working PHP/AJAX contact form: https://bootstrapmade.com/personal-free-resume-bootstrap-template/ -->
    Designed by <a href="https://bootstrapmade.com/">BootstrapMade</a>
  </div>
  <span>© {% now "Y" %} {{ personal_info.name }} · Handcrafted with Python & Django</span>
</div>
```

## templates/base/style.html
```
{% load static %}
<!-- Vendor CSS Files -->
<link href="{% static 'vendor/bootstrap/css/bootstrap.min.css' %}" rel="stylesheet">
<link href="{% static 'vendor/bootstrap-icons/bootstrap-icons.css' %}" rel="stylesheet">
<link href="{% static 'vendor/boxicons/css/boxicons.min.css' %}" rel="stylesheet">
<link href="{% static 'vendor/glightbox/css/glightbox.min.css' %}" rel="stylesheet">
<link href="{% static 'vendor/remixicon/remixicon.css' %}" rel="stylesheet">
<link href="{% static 'vendor/swiper/swiper-bundle.min.css' %}" rel="stylesheet">

<!-- Template Main CSS File -->
<link href="{% static 'css/style.css' %}" rel="stylesheet">

```

## templates/base/script.html
```
{% load static %}
<!-- Vendor JS Files -->
<script src="{% static 'vendor/purecounter/purecounter_vanilla.js' %}"></script>
<script src="{% static 'vendor/bootstrap/js/bootstrap.bundle.min.js' %}"></script>
<script src="{% static 'vendor/glightbox/js/glightbox.min.js' %}"></script>
<script src="{% static 'vendor/isotope-layout/isotope.pkgd.min.js' %}"></script>
<script src="{% static 'vendor/swiper/swiper-bundle.min.js' %}"></script>
<script src="{% static 'vendor/waypoints/noframework.waypoints.js' %}"></script>
<script src="{% static 'vendor/php-email-form/validate.js' %}"></script>

<!-- Template Main JS File -->
<script src="{% static 'js/main.js' %}"></script>
```