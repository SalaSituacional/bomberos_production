from django.shortcuts import render, redirect, get_object_or_404


def Dashboard_pov(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "pov/dashboardPov.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })


def Tabla_pov(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "pov/tablaPov.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })

