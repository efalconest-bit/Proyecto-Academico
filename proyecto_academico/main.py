from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
import views


def pedir_entero(texto):
    try:
        return int(input(texto).strip())
    except ValueError:
        imprimir_error("Escriba un número entero válido.")
        return None


def pedir_texto(texto):
    return input(texto).strip()


def mostrar_lista(registros, titulo):
    imprimir_titulo(titulo)
    if not registros:
        imprimir_info("No hay registros.")
    else:
        # Polimorfismo: cada modelo se presenta con su propia etiqueta().
        for registro in registros:
            print(registro)
    input("\nPresione Enter para continuar...")


def mostrar_resultado(resultado):
    exito, mensaje = resultado
    (imprimir_exito if exito else imprimir_error)(mensaje)
    input("\nPresione Enter para continuar...")


def menu_estudiantes():
    while True:
        imprimir_titulo("GESTIÓN DE ESTUDIANTES")
        print("1. Crear estudiante")
        print("2. Ver todos")
        print("3. Buscar")
        print("4. Ver por ID")
        print("5. Actualizar")
        print("6. Eliminar")
        print("0. Volver")
        op = pedir_texto("Opción: ")
        if op == "0":
            return
        elif op == "1":
            datos = {
                "nombre": pedir_texto("Nombre: "),
                "apellido": pedir_texto("Apellido: "),
                "email": pedir_texto("Correo: "),
                "carnet": pedir_texto("Carnet: "),
                "carrera": pedir_texto("Carrera: ")
            }
            mostrar_resultado(views.crear_estudiante(datos))
        elif op == "2":
            mostrar_lista(views.obtener_estudiantes(), "ESTUDIANTES")
        elif op == "3":
            mostrar_lista(views.buscar_estudiantes(pedir_texto("Texto a buscar: ")), "RESULTADOS")
        elif op == "4":
            id_registro = pedir_entero("ID: ")
            if id_registro is not None:
                estudiante = views.obtener_estudiante(id_registro)
                mostrar_lista([estudiante] if estudiante else [], "ESTUDIANTE")
        elif op == "5":
            id_registro = pedir_entero("ID a actualizar: ")
            if id_registro is not None:
                actual = views.obtener_estudiante(id_registro)
                if not actual:
                    mostrar_resultado((False, "No existe ese estudiante."))
                    continue
                datos = {
                    "nombre": pedir_texto(f"Nombre [{actual.nombre}]: ") or actual.nombre,
                    "apellido": pedir_texto(f"Apellido [{actual.apellido}]: ") or actual.apellido,
                    "email": pedir_texto(f"Correo [{actual.email}]: ") or actual.email,
                    "carnet": pedir_texto(f"Carnet [{actual.carnet}]: ") or actual.carnet,
                    "carrera": pedir_texto(f"Carrera [{actual.carrera}]: ") or actual.carrera
                }
                mostrar_resultado(views.actualizar_estudiante(id_registro, datos))
        elif op == "6":
            id_registro = pedir_entero("ID a eliminar: ")
            if id_registro is not None and confirmar("¿Confirma la eliminación?"):
                mostrar_resultado(views.eliminar_estudiante(id_registro))
        else:
            imprimir_error("Opción no válida.")
            input("Enter para continuar...")


def menu_materias():
    while True:
        imprimir_titulo("GESTIÓN DE MATERIAS")
        print("1. Crear materia")
        print("2. Ver todas")
        print("3. Buscar")
        print("4. Ver por ID")
        print("5. Actualizar")
        print("6. Eliminar")
        print("7. Ver materias sin cupo")
        print("0. Volver")
        op = pedir_texto("Opción: ")
        if op == "0":
            return
        elif op == "1":
            datos = {
                "nombre": pedir_texto("Nombre: "),
                "codigo": pedir_texto("Código: "),
                "creditos": pedir_entero("Créditos (1-10): "),
                "cupos": pedir_entero("Cupos (0-30): ")
            }
            if None in (datos["creditos"], datos["cupos"]):
                input("Enter para continuar...")
            else:
                mostrar_resultado(views.crear_materia(datos))
        elif op == "2":
            mostrar_lista(views.obtener_materias(), "MATERIAS")
        elif op == "3":
            mostrar_lista(views.buscar_materias(pedir_texto("Texto a buscar: ")), "RESULTADOS")
        elif op == "4":
            id_registro = pedir_entero("ID: ")
            if id_registro is not None:
                materia = views.obtener_materia(id_registro)
                mostrar_lista([materia] if materia else [], "MATERIA")
        elif op == "5":
            id_registro = pedir_entero("ID a actualizar: ")
            if id_registro is not None:
                actual = views.obtener_materia(id_registro)
                if not actual:
                    mostrar_resultado((False, "No existe esa materia."))
                    continue
                datos = {
                    "nombre": pedir_texto(f"Nombre [{actual.nombre}]: ") or actual.nombre,
                    "codigo": pedir_texto(f"Código [{actual.codigo}]: ") or actual.codigo,
                    "creditos": pedir_entero(f"Créditos [{actual.creditos}]: "),
                    "cupos": pedir_entero(f"Cupos disponibles [{actual.cupos}]: ")
                }
                if datos["creditos"] is None:
                    datos["creditos"] = actual.creditos
                if datos["cupos"] is None:
                    datos["cupos"] = actual.cupos
                mostrar_resultado(views.actualizar_materia(id_registro, datos))
        elif op == "6":
            id_registro = pedir_entero("ID a eliminar: ")
            if id_registro is not None and confirmar("¿Confirma la eliminación?"):
                mostrar_resultado(views.eliminar_materia(id_registro))
        elif op == "7":
            mostrar_lista(views.materias_sin_cupo(), "MATERIAS SIN CUPO")
        else:
            imprimir_error("Opción no válida.")
            input("Enter para continuar...")


def menu_matriculas():
    while True:
        imprimir_titulo("GESTIÓN DE MATRÍCULAS")
        print("1. Matricular estudiante")
        print("2. Ver todas")
        print("3. Registrar nota")
        print("4. Ver certificado")
        print("5. Retirar matrícula")
        print("0. Volver")
        op = pedir_texto("Opción: ")
        if op == "0":
            return
        elif op == "1":
            estudiante_id = pedir_entero("ID del estudiante: ")
            materia_id = pedir_entero("ID de la materia: ")
            periodo = pedir_texto("Período (ej. 2026-1): ")
            if estudiante_id is not None and materia_id is not None:
                mostrar_resultado(views.crear_matricula({
                    "estudiante_id": estudiante_id,
                    "materia_id": materia_id,
                    "periodo": periodo
                }))
            else:
                input("Enter para continuar...")
        elif op == "2":
            mostrar_lista(views.obtener_matriculas(), "MATRÍCULAS")
        elif op == "3":
            id_registro = pedir_entero("ID de matrícula: ")
            if id_registro is not None:
                nota = pedir_texto("Nota (0-20): ")
                mostrar_resultado(views.registrar_nota(id_registro, nota))
        elif op == "4":
            id_registro = pedir_entero("ID de matrícula: ")
            if id_registro is not None:
                resultado = views.certificado(id_registro)
                imprimir_titulo("CERTIFICADO ACADÉMICO")
                if not resultado:
                    imprimir_error("No existe esa matrícula.")
                else:
                    matricula, estudiante, materia = resultado
                    if estudiante and materia:
                        print(f"CERTIFICADO #{matricula.id}   período: {matricula.periodo}")
                        print(f"Estudiante: {estudiante.nombre_completo()} ({estudiante.carnet})")
                        print(f"Materia   : {materia.nombre} ({materia.codigo}) · {materia.creditos} créditos")
                        print("-" * 45)
                        print(f"Nota      : {matricula.nota if matricula.nota is not None else 'Pendiente'}")
                        print(f"Estado    : {matricula.estado()}")
                    else:
                        imprimir_error("Faltan datos relacionados para mostrar el certificado.")
                input("\nPresione Enter para continuar...")
        elif op == "5":
            id_registro = pedir_entero("ID de matrícula a retirar: ")
            if id_registro is not None and confirmar("¿Confirma retirar la matrícula?"):
                mostrar_resultado(views.retirar_matricula(id_registro))
        else:
            imprimir_error("Opción no válida.")
            input("Enter para continuar...")


def mostrar_resumen():
    datos = views.resumen()
    imprimir_titulo("RESUMEN ACADÉMICO")
    print(f"Total de estudiantes: {datos['estudiantes']}")
    print("Carreras distintas:", ", ".join(datos["carreras"]) if datos["carreras"] else "Ninguna")
    print("Materias sin cupo:")
    if datos["materias_sin_cupo"]:
        for materia in datos["materias_sin_cupo"]:
            print(f"  - {materia.nombre} ({materia.codigo})")
    else:
        print("  Ninguna")
    print(f"Matrículas aprobadas: {datos['matriculas_aprobadas']}")
    input("\nPresione Enter para continuar...")


def main():
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO")
        print("1. Estudiantes")
        print("2. Materias")
        print("3. Matrículas")
        print("4. Resumen")
        print("0. Salir")
        opcion = pedir_texto("Seleccione una opción: ")
        if opcion == "1":
            menu_estudiantes()
        elif opcion == "2":
            menu_materias()
        elif opcion == "3":
            menu_matriculas()
        elif opcion == "4":
            mostrar_resumen()
        elif opcion == "0":
            print("Hasta pronto.")
            break
        else:
            imprimir_error("Opción no válida.")
            input("Presione Enter para continuar...")


if __name__ == "__main__":
    main()
