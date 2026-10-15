from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
# Solo dice QUÉ métodos debe tener todo controlador.
# CÓMO se hace cada uno lo escribe cada controlador, de la forma más simple.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE ESTUDIANTES
# =====================================================================
class EstudianteController(CrudBase):

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for estudiante in self.lista:
            datos.append(estudiante.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Devuelve un mensaje de error, o None si todo está bien."""
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        for campo in ("nombre", "apellido", "carnet"):
            if campo in datos and str(datos[campo]).strip() == "":
                return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO: consulta rápida de los emails usados por otros estudiantes.
            usados = {e.email.lower() for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        if "carnet" in datos or id_actual is None:
            carnet = str(datos.get("carnet", "")).strip().upper()
            # CONJUNTO: evita que dos estudiantes tengan el mismo carnet.
            usados = {e.carnet.upper() for e in self.lista if e.id != id_actual}
            if carnet in usados:
                return "Ese carnet ya está registrado"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        # CONJUNTO: permite comprobar rápidamente si ese id está registrado.
        ids = {estudiante.id for estudiante in self.lista}
        if id_estudiante not in ids:
            return None
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        # TUPLA: los campos buscables son fijos y no deben modificarse.
        campos = ("nombre", "apellido", "email", "carnet", "carrera")
        for estudiante in self.lista:
            for campo in campos:
                if texto in str(getattr(estudiante, campo, "")).lower():
                    encontrados.append(estudiante)
                    break
        return encontrados

    def siguiente(self):
        mayor = 0
        for estudiante in self.lista:
            if estudiante.id > mayor:
                mayor = estudiante.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos["carnet"]).strip().upper(),
            str(datos.get("carrera", "")).strip().title())
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    # --- propio de estudiantes ---
    def carreras(self):
        """CONJUNTO: devuelve carreras distintas sin repetir, ordenadas para mostrarlas."""
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


# =====================================================================
# CONTROLADOR DE MATERIAS
# =====================================================================
class MateriaController(CrudBase):

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for materia in self.lista:
            datos.append(materia.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "creditos" in datos or id_actual is None:
            try:
                creditos = int(datos.get("creditos", 0))
            except (TypeError, ValueError):
                return "Los créditos deben ser un número entero entre 1 y 10"
            if not 1 <= creditos <= 10:
                return "Los créditos deben estar entre 1 y 10"

        if "cupos" in datos or id_actual is None:
            try:
                cupos = int(datos.get("cupos", 0))
            except (TypeError, ValueError):
                return "Los cupos deben ser un número entero entre 0 y 30"
            if not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
                return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"

        for campo in ("nombre", "codigo"):
            if campo in datos and str(datos[campo]).strip() == "":
                return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            # CONJUNTO: evita códigos de materia repetidos.
            usados = {m.codigo.upper() for m in self.lista if m.id != id_actual}
            if codigo in usados:
                return "Ese código de materia ya está registrado"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otra in self.lista:
                if otra.nombre == nombre and otra.id != id_actual:
                    return f"Ya existe una materia llamada {nombre}"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        # CONJUNTO: permite comprobar rápidamente si ese id está registrado.
        ids = {materia.id for materia in self.lista}
        if id_materia not in ids:
            return None
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas
        # TUPLA: estos son los campos fijos que se pueden buscar.
        campos = ("nombre", "codigo")
        for materia in self.lista:
            for campo in campos:
                if texto in str(getattr(materia, campo, "")).lower():
                    encontradas.append(materia)
                    break
        return encontradas

    def siguiente(self):
        mayor = 0
        for materia in self.lista:
            if materia.id > mayor:
                mayor = materia.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            int(datos["creditos"]),
            int(datos.get("cupos", 0)))
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    # --- propio de materias ---
    def materias_sin_cupo(self):
        """Lista de materias en las que ya no quedan cupos."""
        return [materia for materia in self.lista if not materia.hay_cupo()]


# =====================================================================
# CONTROLADOR DE MATRÍCULAS
# =====================================================================
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        # La matrícula USA a los otros dos controladores, igual que Venta.
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for matricula in self.lista:
            datos.append(matricula.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "El id del estudiante y el id de la materia deben ser enteros"

        periodo = str(datos.get("periodo", "")).strip()
        if periodo == "":
            return "El periodo es obligatorio"

        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe un estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe una materia con id {materia_id}"
        if not materia.hay_cupo():
            return f"La materia {materia.nombre} no tiene cupos disponibles"

        # La combinación completa debe ser única: estudiante + materia + periodo.
        for otra in self.lista:
            if (otra.id != id_actual and otra.estudiante_id == estudiante_id
                    and otra.materia_id == materia_id and otra.periodo.lower() == periodo.lower()):
                return "El estudiante ya está matriculado en esa materia durante ese periodo"

        if "nota" in datos and not Materia.es_nota_valida(datos["nota"]):
            return "La nota debe ser un número entre 0 y 20"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        # CONJUNTO: permite comprobar rápidamente si ese id está registrado.
        ids = {matricula.id for matricula in self.lista}
        if id_matricula not in ids:
            return None
        for matricula in self.lista:
            if matricula.id == id_matricula:
                return matricula
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas
        # TUPLA: define los campos fijos por los que se buscan matrículas.
        campos = ("periodo", "fecha", "estado")
        for matricula in self.lista:
            for campo in campos:
                valor = matricula.estado() if campo == "estado" else getattr(matricula, campo, "")
                if texto in str(valor).lower():
                    encontradas.append(matricula)
                    break
        return encontradas

    def siguiente(self):
        mayor = 0
        for matricula in self.lista:
            if matricula.id > mayor:
                mayor = matricula.id
        return mayor + 1

    def crear(self, datos):
        return self.crear_matricula(datos)

    def crear_matricula(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante_id = int(datos["estudiante_id"])
        materia = self.materias.obtener(int(datos["materia_id"]))
        nota = float(datos.get("nota", 0))
        matricula = Matricula(self.siguiente(), estudiante_id, materia.id,
                              str(datos["periodo"]).strip(), nota)

        # El cupo se ocupa y se guarda en materias.json antes de guardar la matrícula.
        materia.ocupar_cupo()
        self.materias.guardar()
        self.lista.append(matricula)
        self.guardar()
        return True, f"Matrícula {matricula.id} registrada: {matricula.etiqueta()}"

    def actualizar(self, id_matricula, datos):
        return False, "Use la opción Registrar nota para cambiar la nota de una matrícula"

    def registrar_nota(self, id_matricula, nota):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"
        if not Materia.es_nota_valida(nota):
            return False, "La nota debe ser un número entre 0 y 20"
        matricula.nota = float(nota)
        self.guardar()
        return True, f"Nota registrada. Estado: {matricula.estado()}"

    def eliminar(self, id_matricula):
        return self.retirar_matricula(id_matricula)

    def retirar_matricula(self, id_matricula):
        """Retira una matrícula y devuelve el cupo a la materia."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula {id_matricula} retirada y cupo devuelto"

    # --- propios de matrículas ---
    def certificado(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None

        # DICCIONARIOS ÍNDICE: permiten cruzar ids con objetos directamente.
        estudiantes_por_id = {e.id: e for e in self.estudiantes.leer()}
        materias_por_id = {m.id: m for m in self.materias.leer()}
        estudiante = estudiantes_por_id.get(matricula.estudiante_id)
        materia = materias_por_id.get(matricula.materia_id)

        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        texto += f"Estudiante: {estudiante.nombre_completo() if estudiante else 'eliminado'}"
        if estudiante:
            texto += f"   ({estudiante.carnet})"
        texto += "\n"
        if materia:
            texto += f"Materia   : {materia.nombre}   ({materia.codigo}) · {materia.creditos} créditos\n"
        else:
            texto += "Materia   : eliminada\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {matricula.nota:g}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        """DICCIONARIO DE LISTAS: agrupa matrículas por estudiante; setdefault crea la lista."""
        agrupadas = {}
        for matricula in self.lista:
            agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        notas = [m.nota for m in self.lista if m.estudiante_id == id_estudiante]
        if not notas:
            return None
        return round(sum(notas) / len(notas), 2)

    def aprobadas(self):
        return [matricula for matricula in self.lista if matricula.esta_aprobada()]
