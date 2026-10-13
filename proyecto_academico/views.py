import os
from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

# Las rutas se resuelven desde la carpeta del proyecto.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
gestor_estudiantes = GestorJSON(os.path.join(BASE_DIR, "data", "estudiantes.json"))
gestor_materias = GestorJSON(os.path.join(BASE_DIR, "data", "materias.json"))
gestor_matriculas = GestorJSON(os.path.join(BASE_DIR, "data", "matriculas.json"))


def leer_objetos(gestor, modelo):
    """Convierte cada diccionario del JSON en un objeto del modelo."""
    return [modelo.desde_diccionario(d) for d in gestor.leer()]


def guardar_objetos(gestor, objetos):
    """Convierte objetos a diccionarios y los guarda."""
    return gestor.guardar([obj.a_diccionario() for obj in objetos])


def obtener_por_id(objetos, id_registro):
    for objeto in objetos:
        if objeto.id == int(id_registro):
            return objeto
    return None


def buscar(objetos, termino, campos):
    # Tupla: los campos buscables son una selección fija.
    termino = str(termino).strip().lower()
    return [
        obj for obj in objetos
        if any(termino in str(getattr(obj, campo, "")).lower()
               for campo in campos)
    ]


def siguiente_id(gestor):
    registros = gestor.leer()
    # La lista se recorre para obtener el máximo ID actual.
    return max((r.get("id", 0) for r in registros), default=0) + 1


def ids_registrados(gestor, campo, excepto_id=None):
    # Conjunto: evita duplicados y hace eficiente la consulta de pertenencia.
    return {
        str(r.get(campo, "")).strip().upper()
        for r in gestor.leer() if r.get("id") != excepto_id
    }


def guardar_nuevo(gestor, objeto):
    objetos = leer_objetos(gestor, type(objeto))
    objetos.append(objeto)
    return guardar_objetos(gestor, objetos)


def reemplazar(gestor, objeto):
    objetos = leer_objetos(gestor, type(objeto))
    for indice, actual in enumerate(objetos):
        if actual.id == objeto.id:
            objetos[indice] = objeto
            return guardar_objetos(gestor, objetos)
    return False


def eliminar(gestor, id_registro):
    # Comprensión de lista: crea una lista nueva sin el registro seleccionado.
    datos = [r for r in gestor.leer() if r.get("id") != int(id_registro)]
    if len(datos) == len(gestor.leer()):
        return False
    return gestor.guardar(datos)


def validar_estudiante(datos, id_actual=None):
    obligatorios = ("nombre", "apellido", "email", "carnet", "carrera")
    if any(not str(datos.get(campo, "")).strip() for campo in obligatorios):
        return "Todos los campos del estudiante son obligatorios."
    if not es_email_valido(datos["email"]):
        return "El correo electrónico no tiene un formato válido."
    carnet = datos["carnet"].strip().upper()
    email = datos["email"].strip().lower()
    for r in gestor_estudiantes.leer():
        if r.get("id") == id_actual:
            continue
        if r.get("carnet", "").strip().upper() == carnet:
            return "Ya existe un estudiante con ese carnet."
        if r.get("email", "").strip().lower() == email:
            return "Ya existe un estudiante con ese correo."
    return None


def crear_estudiante(datos):
    error = validar_estudiante(datos)
    if error:
        return False, error
    estudiante = Estudiante(siguiente_id(gestor_estudiantes), **datos)
    if guardar_nuevo(gestor_estudiantes, estudiante):
        return True, "Estudiante creado correctamente."
    return False, "No se pudo guardar el estudiante."


def obtener_estudiantes():
    return leer_objetos(gestor_estudiantes, Estudiante)


def obtener_estudiante(id_registro):
    return obtener_por_id(obtener_estudiantes(), id_registro)


def buscar_estudiantes(termino):
    return buscar(obtener_estudiantes(), termino, ("nombre", "apellido", "email", "carnet", "carrera"))


def actualizar_estudiante(id_registro, cambios):
    actual = obtener_estudiante(id_registro)
    if not actual:
        return False, "No existe un estudiante con ese ID."
    datos = actual.a_diccionario()
    datos.update(cambios)
    error = validar_estudiante(datos, int(id_registro))
    if error:
        return False, error
    actualizado = Estudiante.desde_diccionario(datos)
    return (True, "Estudiante actualizado.") if reemplazar(gestor_estudiantes, actualizado) else (False, "No se pudo guardar.")


def eliminar_estudiante(id_registro):
    if any(m.estudiante_id == int(id_registro) for m in obtener_matriculas()):
        return False, "No se puede eliminar: el estudiante tiene matrículas registradas."
    if eliminar(gestor_estudiantes, id_registro):
        return True, "Estudiante eliminado."
    return False, "No existe ese estudiante."


def validar_materia(datos, id_actual=None):
    for campo in ("nombre", "codigo"):
        if not str(datos.get(campo, "")).strip():
            return "El nombre y el código de la materia son obligatorios."
    try:
        creditos, cupos = int(datos["creditos"]), int(datos["cupos"])
    except (ValueError, TypeError, KeyError):
        return "Créditos y cupos deben ser números enteros."
    if not 1 <= creditos <= 10:
        return "Los créditos deben estar entre 1 y 10."
    if not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
        return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}."
    codigo = datos["codigo"].strip().upper()
    for r in gestor_materias.leer():
        if r.get("id") != id_actual and r.get("codigo", "").upper() == codigo:
            return "Ya existe una materia con ese código."
    return None


def crear_materia(datos):
    error = validar_materia(datos)
    if error:
        return False, error
    materia = Materia(siguiente_id(gestor_materias), **datos)
    if guardar_nuevo(gestor_materias, materia):
        return True, "Materia creada correctamente."
    return False, "No se pudo guardar la materia."


def obtener_materias():
    return leer_objetos(gestor_materias, Materia)


def obtener_materia(id_registro):
    return obtener_por_id(obtener_materias(), id_registro)


def buscar_materias(termino):
    return buscar(obtener_materias(), termino, ("nombre", "codigo"))


def actualizar_materia(id_registro, cambios):
    actual = obtener_materia(id_registro)
    if not actual:
        return False, "No existe una materia con ese ID."
    datos = actual.a_diccionario()
    datos.update(cambios)
    error = validar_materia(datos, int(id_registro))
    if error:
        return False, error
    # No permite cambiar cupos por debajo de los que ya están ocupados.
    matriculas_activas = sum(1 for m in obtener_matriculas() if m.materia_id == actual.id)
    if int(datos["cupos"]) + matriculas_activas > Materia.CUPOS_MAXIMOS:
        return False, "Los cupos más las matrículas existentes superan el máximo de 30."
    actualizado = Materia.desde_diccionario(datos)
    return (True, "Materia actualizada.") if reemplazar(gestor_materias, actualizado) else (False, "No se pudo guardar.")


def eliminar_materia(id_registro):
    if any(m.materia_id == int(id_registro) for m in obtener_matriculas()):
        return False, "No se puede eliminar: la materia tiene matrículas registradas."
    if eliminar(gestor_materias, id_registro):
        return True, "Materia eliminada."
    return False, "No existe esa materia."


def materias_sin_cupo():
    return [m for m in obtener_materias() if not m.hay_cupo()]


def obtener_matriculas():
    return leer_objetos(gestor_matriculas, Matricula)


def obtener_matricula(id_registro):
    return obtener_por_id(obtener_matriculas(), id_registro)


def crear_matricula(datos):
    try:
        estudiante_id = int(datos["estudiante_id"])
        materia_id = int(datos["materia_id"])
        periodo = str(datos["periodo"]).strip()
    except (ValueError, TypeError, KeyError):
        return False, "Estudiante, materia y período son obligatorios."

    estudiante = obtener_estudiante(estudiante_id)
    materia = obtener_materia(materia_id)
    if not estudiante:
        return False, "El estudiante indicado no existe."
    if not materia:
        return False, "La materia indicada no existe."
    if not periodo:
        return False, "El período es obligatorio."
    if not materia.hay_cupo():
        return False, "La materia no tiene cupos disponibles."

    # No se permiten dos matrículas del mismo estudiante, materia y período.
    for m in obtener_matriculas():
        if (m.estudiante_id == estudiante_id and m.materia_id == materia_id
                and m.periodo.lower() == periodo.lower()):
            return False, "El estudiante ya está matriculado en esa materia y período."

    matricula = Matricula(siguiente_id(gestor_matriculas), estudiante_id, materia_id, periodo)
    materia.ocupar_cupo()
    if not reemplazar_o_guardar_materia(materia):
        return False, "No se pudo actualizar el cupo de la materia."
    if not guardar_nuevo(gestor_matriculas, matricula):
        materia.liberar_cupo()
        reemplazar_o_guardar_materia(materia)
        return False, "No se pudo guardar la matrícula; se restauró el cupo."
    return True, f"Matrícula creada con ID {matricula.id}."


def reemplazar_o_guardar_materia(materia):
    if obtener_materia(materia.id):
        return reemplazar(gestor_materias, materia)
    return guardar_nuevo(gestor_materias, materia)


def registrar_nota(id_registro, nota):
    matricula = obtener_matricula(id_registro)
    if not matricula:
        return False, "No existe esa matrícula."
    if not Materia.es_nota_valida(nota):
        return False, "La nota debe ser un número entre 0 y 20."
    matricula.nota = float(nota)
    return (True, "Nota registrada.") if reemplazar(gestor_matriculas, matricula) else (False, "No se pudo guardar la nota.")


def retirar_matricula(id_registro):
    matricula = obtener_matricula(id_registro)
    if not matricula:
        return False, "No existe esa matrícula."
    materia = obtener_materia(matricula.materia_id)
    if materia:
        materia.liberar_cupo()
        if not reemplazar(gestor_materias, materia):
            return False, "No se pudo liberar el cupo."
    if eliminar(gestor_matriculas, id_registro):
        return True, "Matrícula retirada y cupo liberado."
    return False, "No se pudo retirar la matrícula."


def certificado(id_registro):
    matricula = obtener_matricula(id_registro)
    if not matricula:
        return None
    # Diccionario índice: permite localizar estudiante y materia por ID.
    estudiantes_por_id = {e.id: e for e in obtener_estudiantes()}
    materias_por_id = {m.id: m for m in obtener_materias()}
    estudiante = estudiantes_por_id.get(matricula.estudiante_id)
    materia = materias_por_id.get(matricula.materia_id)
    return matricula, estudiante, materia


def matriculas_por_estudiante():
    # Diccionario de listas: agrupa las matrículas bajo el ID de cada estudiante.
    agrupadas = {}
    for matricula in obtener_matriculas():
        agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
    return agrupadas


def promedio_de_estudiante(id_estudiante):
    notas = [m.nota for m in matriculas_por_estudiante().get(int(id_estudiante), [])
             if m.nota is not None]
    return round(sum(notas) / len(notas), 2) if notas else None


def resumen():
    estudiantes = obtener_estudiantes()
    carreras = sorted({e.carrera for e in estudiantes if e.carrera})
    matriculas = obtener_matriculas()
    return {
        "estudiantes": len(estudiantes),
        "carreras": carreras,
        "materias_sin_cupo": materias_sin_cupo(),
        "matriculas_aprobadas": sum(1 for m in matriculas if m.esta_aprobada())
    }
