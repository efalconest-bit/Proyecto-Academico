from datetime import date


# =====================================================================
# CLASE BASE: lo que los tres modelos comparten
# =====================================================================
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento común."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    # ---- ÚNICO MÉTODO DE CLASE DEL PROYECTO ----
    @classmethod
    def desde_diccionario(cls, datos):
        """Diccionario -> objeto. Escrito UNA vez y usado por los tres modelos.
        cls es la clase que llamó: Cliente, Producto o Venta."""
        datos = dict(datos)                 # copia, para no tocar el original
        id_registro = datos.pop("id")       # saco el id
        return cls(id_registro, **datos)    # el resto son los campos del modelo

    # ---- MÉTODOS DE INSTANCIA ----
    def a_diccionario(self):
        # Objeto -> diccionario. Cada hijo agrega sus campos.
        return {"id": self.id}

    def etiqueta(self):
        # POLIMORFISMO: cada hijo la reescribe a su manera
        return f"registro {self.id}"

    def __str__(self):
        # Lo que se ve al hacer print(objeto). Llama a etiqueta(),
        # así que cada modelo se imprime distinto sin cambiar esta línea.
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona es la base de Cliente (y mañana, de Estudiante)
# =====================================================================
class Persona(ModeloBase):
    """Todo lo que tiene una persona del sistema."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)      # el padre guarda el id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()    # {"id": ...} que arma el padre
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona, con carnet y carrera."""

    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self):
        datos = super().a_diccionario()    # reutiliza id, nombre, apellido y email
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        # Sobrescribe y EXTIENDE la etiqueta del padre
        return f"{super().etiqueta()} · {self.carnet} · {self.carrera or 'sin carrera'}"


# =====================================================================
# ÚNICA CLASE CON ATRIBUTOS Y MÉTODOS ESTÁTICOS DEL NEGOCIO
# =====================================================================
class Materia(ModeloBase):
    """Materia ES UN ModeloBase. Aquí viven las reglas estáticas académicas."""

    # ATRIBUTOS ESTÁTICOS (de clase): existen una sola vez, no por objeto
    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14
    total_creadas = 0         # contador compartido, igual que en el proyecto de ventas

    def __init__(self, id_registro, nombre, codigo, creditos=0, cupos=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = int(creditos)
        self.cupos = int(cupos)
        Materia.total_creadas += 1

    # MÉTODO ESTÁTICO: valida una nota sin necesitar una materia concreta
    @staticmethod
    def es_nota_valida(valor):
        try:
            return 0 <= float(valor) <= 20
        except (TypeError, ValueError):
            return False

    # MÉTODOS DE INSTANCIA: necesitan los datos de ESTA materia
    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if self.hay_cupo():
            self.cupos -= 1
            return True
        return False

    def liberar_cupo(self):
        if self.cupos < Materia.CUPOS_MAXIMOS:
            self.cupos += 1
            return True
        return False

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self):
        alerta = " · SIN CUPOS" if not self.hay_cupo() else ""
        return f"{self.nombre} · {self.codigo} · {self.creditos} créditos · cupos {self.cupos}{alerta}"


# =====================================================================
class Matricula(ModeloBase):
    """Matrícula simple: un estudiante, una materia y un periodo."""

    def __init__(self, id_registro, estudiante_id, materia_id, periodo,
                 nota=0, fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = str(periodo).strip()
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self):
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        # Se calcula cada vez; no se guarda en el JSON.
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        return (f"{self.fecha} · estudiante {self.estudiante_id} · "
                f"materia {self.materia_id} · periodo {self.periodo} · "
                f"nota {self.nota:g} ({self.estado()})")
