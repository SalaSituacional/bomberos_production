import instaloader
from web.models import InstagramPost  # Asegúrate de importar tu modelo de InstagramPost

def save_instagram_posts(profile_name, num_posts=20):
    # Crear un objeto Instaloader
    L = instaloader.Instaloader()

    # Iniciar sesión si lo necesitas (solo si el perfil es privado)
    # L.context.log("Iniciando sesión...")
    # L.load_session_from_file("my_username")  # si ya tienes una sesión guardada
    # L.context.log("Sesión cargada!")

    # Obtener el perfil
    profile = instaloader.Profile.from_username(L.context, profile_name)

    # Iterar a través de las publicaciones y guardar las URLs y fechas
    posts = profile.get_posts()
    count = 0

    for post in posts:
        if count >= num_posts:
            break

        # Obtener el shortcode de la publicación para generar la URL
        shortcode = post.shortcode  # El shortcode de la publicación
        post_url = f'https://www.instagram.com/p/{shortcode}/'  # Construir la URL completa de la publicación
        
        # Obtener la fecha de la publicación (en formato UTC)
        post_date = post.date_utc  # Fecha y hora de la publicación en UTC

        # Guardar la URL y la fecha en la base de datos
        InstagramPost.objects.create(url=post_url, fecha=post_date)
        count += 1

    print(f"Se han guardado {count} publicaciones de Instagram de {profile_name}.")

