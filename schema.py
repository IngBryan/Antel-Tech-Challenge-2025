import os
from dotenv import load_dotenv,dotenv_values
from pydantic import BaseModel, Field


load_dotenv(dotenv_path="./Config.env")
config = dotenv_values()

nivel_str = os.getenv("NIVEL_DEL_SERVICIO")
nivel_servicio = tuple(map(int, nivel_str.split("/"))) #(80,20)




class Incidencia(BaseModel):
    fecha: str = Field(description="Fecha de incidencia en formato XX-XX-XX.")
    motivo: str = Field(description="Resumen del motivo de la incidencia.")


class Reclamos(BaseModel):
    # campania: str = Field(description="Por ejemplo Reclamos_611")
    manejo: int = Field(
        title="Manejo",
        description='Total cantidad de llamadas al Sistema de Reclamos de ANTEL. Se obtiene de la columna "Manejo"',
    )
    manejo_total: str = Field(
        title="Manejo Total",
        description='Se obtiene en la columna "Manejo total"',
    )


class MotivoIZI611(BaseModel):
    nombre_de_codigo_de_conclusion: str = Field(
        title="Nombre de código de conclusión",
        description='Se obtiene en la columna "Nombre de código de conclusión", por ejemplo "Información General - 611", "Cliente no responde - 611", "Facturacion - 611"',
    )
    manejo: int = Field(
        title="Manejo",
        description='Se obtiene en la columna "Manejo"',
    )


class AntelMovil611(BaseModel):
    llamadas_al_servicio: int = Field(
        description="Se calcula a partir de “Listado de llamadas Atendidas y Abandonadas - Habilidad/Fecha” como la suma total de los valores de la columna “Ofrecidas”. Observar que este valor debe coincidir con el que se encuentra en la columna “Ofrecidas” a partir de “Habilidad” en la fila “ANTEL MOVIL”"
    )
    llamadas_atendidas_totales: int = Field(
        description="se calcula a partir de “Listado de llamadas Atendidas y Abandonadas - Habilidad/Fecha” como la suma total de los valores de la columna “Atendidas”.  Observar que este valor debe coincidir con el que se encuentra en la columna “Contestadas” a partir de “Habilidad” en la fila “ANTEL MOVIL”."
    )
    llamadas_abandonadas: int = Field(
        description="se calcula a partir de “Listado de llamadas Atendidas y Abandonadas - Habilidad/Fecha” como la suma total de los valores de la columna “Abandonada”. Observar que este valor debe coincidir con el que se encuentra en la columna “Abandonadas” a partir de “Habilidad” en la fila “ANTEL MOVIL”."
    )
    porcentaje_llamadas_no_atendidas: float = Field(
        "se obtiene a partir de “Habilidad” en la fila “ANTEL MOVIL” columna “Indice de Abandono %”"
    )
    cumplimiento_servicio: float = Field(
        description="Porcentaje de cumplimiento del nivel de servicio acordado, donde "+str(nivel_servicio[0])+"%"+ "de nivel de servicio equivale al 100% de cumplimiento. Operación: Nivel de servicio /"+str(nivel_servicio[0])
    )
    indice_respuesta: float = Field(
        description="(Llamadas atendidas totales / Llamadas al servicio) %.  Observar que este valor debe coincidir con el que se encuentra en la columna “Indice de respuesta %” a partir de “Habilidad” en la fila “ANTEL MOVIL”."
    )
    trsac: int = Field(
        description="Demora de atención. La cantidad de segundos que un cliente espera en promedio en ser atendido. Operación: Total de demora en atender(segundos) / Total de llamadas atendidas."
    )
    promedio_operacion: float = Field(
        title="Promedio Operación",
        description="Se obtiene a partir de “Habilidad” en la fila “ANTEL MOVIL” columna “Tiempo Operación”",
    )
    atencion: float = Field(
        title="Tiempo de Atención",
        description="se obtiene a partir de “Habilidad” en la fila “ANTEL MOVIL” columna “Horas Operación”",
    )
    congestion: int = Field(
        description="Cantidad de llamadas que la central devolvió tono ocupado. Operación: Llamadas_con_tono_ocupado / Cantidad_de_intento. Se puede obtener a partir de “Reporte de Calificaciones” en la columna “611(%)” sumando la congestión de cada día, dividiéndola por la cantidad de días."
    )


class Whatsapp(BaseModel):
    entrantes: int = Field(
        title="Cantidad de mensajes entrantes",
        description="se obtiene a partir de “Resumen de Campanas Heynow” en la fila “Roaming” columna “Cantidad de mensajes entrantes”",
    )
    salientes: int = Field(
        title="Cantidad de mensajes salientes",
        description="se obtiene a partir de “Resumen de Campanas Heynow” en la fila “Roaming” columna “Cantidad de mensajes salientes”",
    )
    total: int = Field(
        title="Total de mensajes",
        description="se obtiene a partir de “Resumen de Campanas Heynow” en la fila “Roaming” columna “Total de mensajes”",
    )
    promedio: float = Field(
        title="Promedio de mensajes por interacción",
        description="se obtiene a partir de “Resumen de Campanas Heynow” en la fila “Roaming” columna “Promedio de mensajes por interacción”",
    )


class Salientes(BaseModel):
    movil_contratos: int = Field(
        description="Total de llamadas salientes respecto a MOVIL_Contratos. Se obtiene de la columna “Saliente”."
    )
    movil_prepagos: int = Field(
        description="Total de llamadas salientes respecto a MOVIL_Prepagos. Se obtiene de la columna “Saliente”."
    )
    movil_prioritarios: int = Field(
        description="Total de llamadas salientes respecto a MOVIL_Prioritarios. Se obtiene de la columna “Saliente”."
    )
    salientes_movil: int = Field(
        description="Total de llamadas salientes respecto a Salientes_movil. Se obtiene de la columna “Saliente”."
    )

    @property
    def total(self):
        return (
            self.movil_contratos
            + self.movil_prepagos
            + self.movil_prioritarios
            + self.salientes_movil
        )


class MotivoContacto(BaseModel):
    nombre_cola: str = Field(
        title="Nombre de cola",
        description='Se obtiene de la columna "Nombre de cola". Por ejemplo "MOVIL_Contrato", "MOVIL_Prepago", "MOVIL_Prioritario',
    )
    nombre_de_codigo_de_conclusion: str = Field(
        title="Nombre de código de conclusión",
        description='Se obtiene de la columna "Nombre de código de conclusión", por ejemplo "Información General - 611", "Cliente no responde - 611", "Facturacion - 611".',
    )
    manejo: int = Field(
        title="Manejo",
        description='Se obtiene de la columna "Manejo"',
    )


class MotivosIZI611(BaseModel):
    motivosIzi611: list[MotivoIZI611] = Field(
        description='Lista de valores de la columna "Manejo" para cada "Nombre de código de conclusión". Las filas en este archivo estan duplicadas. Se debe filtrar los datos por la columna “Acumulado o detallado” para utilizar solo "Detallado"'
    )

    @property
    def total(self):
        sum([m.manejo for m in self.motivosIzi611])


class Incidencias(BaseModel):
    incidencias: list[Incidencia] = Field(description="Incidencias relevantes.")


class MotivosContacto(BaseModel):
    motivos_contactos: list[MotivoContacto] = Field(
        description='Lista de motivos de contacto ordenados de forma ascendente según \'Nombre de cola\'. Tener en cuenta solo las filas cuyo valor en la columna "Acumulado o detallado" sea "Detallado"'
    )


class Automatismos(BaseModel):
    exito: int = Field(
        description='Cantidad total de éxito según la columna "Total correcto"'
    )
    error: int = Field(
        description='Cantidad total de errores según la columna "Total error"'
    )

    @property
    def pexito(self):
        return self.exito / self.total

    @property
    def perror(self):
        return self.error / self.total

    @property
    def total(self):
        return self.exito + self.error

    @property
    def ptotal(self):
        return 1.0


class Reporte(BaseModel):
    antel_movil: AntelMovil611
    incidencias: Incidencias
    reclamos: Reclamos
    motivosIzi611: MotivosIZI611
    motivos_contacto: MotivosContacto
    whatsapp: Whatsapp
    salientes: Salientes
    automatismos: Automatismos


if __name__ == "__main__":
    print(Reporte.model_json_schema())
