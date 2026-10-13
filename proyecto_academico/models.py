from datetime import date


class ModeloBase:
    """Clase padre: contiene el identificador y métodos comunes."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos):
        # Método de clase heredado por todos los modelos.
        datos = dict(datos)
        id_registro = datos.pop("id")
        return cls(id_registro, **datos)

    def a_diccionario(self):
        return {"id": self.id}

    def etiqueta(self):
        return f"Registro {self.id}"

    def __str__(self):
        # Polimorfismo: etiqueta() depende del modelo concreto.
        return f"[{self.id}] {self.etiqueta()}"


class Persona(ModeloBase):
    """Clase intermedia para los datos compartidos por personas."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = str(nombre).strip()
        self.apellido = str(apellido).strip()
        self.email = str(email).strip()

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email
        })
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante hereda los datos personales y agrega carnet y carrera."""

    def __init__(self, id_registro, nombre, apellido, email,
                 carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = str(carnet).strip()
        self.carrera = str(carrera).strip()

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.carnet} · {self.carrera}"


class Materia(ModeloBase):
    """Materia administra los créditos y cupos disponibles."""

    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14

    def __init__(self, id_registro, nombre, codigo, creditos=1, cupos=0):
        super().__init__(id_registro)
        self.nombre = str(nombre).strip()
        self.codigo = str(codigo).strip().upper()
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor):
        """Método estático: valida una nota sin necesitar un objeto Materia."""
        try:
            nota = float(valor)
            return 0 <= nota <= 20
        except (TypeError, ValueError):
            return False

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
        datos.update({
            "nombre": self.nombre,
            "codigo": self.codigo,
            "creditos": self.creditos,
            "cupos": self.cupos
        })
        return datos

    def etiqueta(self):
        return (f"{self.nombre} · {self.codigo} · {self.creditos} créditos "
                f"· cupos disponibles: {self.cupos}")


class Matricula(ModeloBase):
    """Relaciona un estudiante con una materia en un período académico."""

    def __init__(self, id_registro, estudiante_id, materia_id,
                 periodo, nota=None, fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = str(periodo).strip()
        self.nota = None if nota in (None, "") else float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self):
        return self.nota is not None and self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        if self.nota is None:
            return "Pendiente"
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "estudiante_id": self.estudiante_id,
            "materia_id": self.materia_id,
            "periodo": self.periodo,
            "nota": self.nota,
            "fecha": self.fecha
        })
        return datos

    def etiqueta(self):
        return (f"Estudiante #{self.estudiante_id} · materia #{self.materia_id} "
                f"· período {self.periodo} · nota {self.nota if self.nota is not None else 'pendiente'} "
                f"· {self.estado()}")
