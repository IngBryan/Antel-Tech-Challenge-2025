import os
from dotenv import load_dotenv, dotenv_values
from pydantic import BaseModel, Field
from typing import Optional


load_dotenv(dotenv_path="../Config.env")
config = dotenv_values()

nivel_str = os.getenv("NIVEL_DEL_SERVICIO")
nivel_servicio = tuple(map(int, nivel_str.split("/")))  # (80,20)


class Incidencia(BaseModel):
    fecha: str = Field(description="Fecha de incidencia en formato XX-XX-XX.")
    motivo: str = Field(description="Resumen del motivo de la incidencia.")
    responsabilidad: str = Field(description="Responsable de la incidencia.")
    descripcion: str = Field(description="Descripción de la incidencia.")

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


class AntelMovilGlobal(BaseModel):
    # SIN EXCEPCION
    llamadas_al_servicio_global: int = Field(
        description="Se calcula a partir de “Listado de llamadas Atendidas y Abandonadas - Habilidad/Fecha” como la suma total de los valores de la columna “Ofrecidas”. Observar que este valor debe coincidir con el que se encuentra en la columna “Ofrecidas” a partir de “Habilidad” en la fila “ANTEL MOVIL”"
    )
    llamadas_atendidas_totales_global: int = Field(
        description="se calcula a partir de “Listado de llamadas Atendidas y Abandonadas - Habilidad/Fecha” como la suma total de los valores de la columna “Atendidas”.  Observar que este valor debe coincidir con el que se encuentra en la columna “Contestadas” a partir de “Habilidad” en la fila “ANTEL MOVIL”."
    )
    llamadas_abandonadas_global: int = Field(
        description="se calcula a partir de “Listado de llamadas Atendidas y Abandonadas - Habilidad/Fecha” como la suma total de los valores de la columna “Abandonada”. Observar que este valor debe coincidir con el que se encuentra en la columna “Abandonadas” a partir de “Habilidad” en la fila “ANTEL MOVIL”."
    )

    @property
    def porcentaje_no_atendidas_global(self):
        return (self.llamadas_abandonadas_global / self.llamadas_al_servicio_global) * 100

    cumplimiento_de_servicio_global: float = Field(
        title="Cumplimiento de Servicio Global",
        description=f"El {nivel_servicio[0]}% de nivel de servicio equivale al 100% de cumplimiento. Operación: Nivel de servicio / {nivel_servicio[0]}%.",
    )
    trsac: int = Field(
        description="Demora de atencion. La cantidad de segundos que un cliente espera en promedio en ser atendido. La operacion es: Total de demora en atender(segundos) / Total de llamadas atendidas."
    )
    promedio_operacion: float = Field(
        title="Promedio Operacion",
        description="Se obtiene a partir de “Habilidad” en la fila “ANTEL MOVIL” columna “Tiempo Operacion",
    )
    atencion: float = Field(
        title="Tiempo de Atencion",
        description="se obtiene a partir de “Habilidad” en la fila “ANTEL MOVIL” columna “Horas Operacion",
    )
    congestion: int = Field(
        description="Cantidad de llamadas que la central devolvio tono ocupado. La operacion es: (Llamadas_con_tono_ocupado / Cantidad_de_intento). Se puede obtener a partir de “Reporte de Calificaciones” en la columna “611(%)” sumando la congesti0n de cada dia, dividiendola por la cantidad de dias."
    )

    @property
    def indice_de_respuesta_global(self):
        return (self.llamadas_atendidas_totales_global / self.llamadas_al_servicio_global)*100
    
    @property
    def porcentaje_cumplimiento_de_servicio_global(self):
        return self.cumplimiento_de_servicio_global*100


class AntelMovilNoGlobal(BaseModel):
    # CON EXCEPCION
    llamadas_al_servicio: int = Field(
        description="Valor de la columna 'Ofrecidas'."
    )
    llamadas_atendidas_totales: int = Field(
        description="Valor de la columna 'Atendidas'."
    )
    llamadas_abandonadas: int = Field(
        description="Valor de la columna 'Abandonadas'."
    )
    llamadas_dentro_del_umbral:int=Field(
        description="Valor de la columna 'Atendidas dentro del umbral'."
    )

    @property
    def nivel_de_servicio(self):
        return (self.llamadas_dentro_del_umbral / self.llamadas_atendidas_totales)*100

    @property
    def cumplimient_nivel_de_servicio(self):
        return self.nivel_de_servicio/(nivel_servicio[0]/100)

    @property
    def porcentaje_no_atendidas(self):
        return (self.llamadas_abandonadas / self.llamadas_al_servicio) * 100

    @property
    def indice_de_respuesta(self):
        return (self.llamadas_atendidas_totales / self.llamadas_al_servicio)*100

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
        description="se obtiene a partir de “Resumen de Campanas Heynow” en la fila “Roaming” columna “Promedio de mensajes por interaccion”",
    )


class Salientes(BaseModel):
    movil_contratos: int = Field(
        description="Total de llamadas salientes respecto al valor MOVIL_Contratos en la columna “Nombre de cola”. Se obtiene de la columna “Saliente”."
    )
    movil_prepagos: int = Field(
        description="Total de llamadas salientes respecto al valor MOVIL_Prepagos en la columna “Nombre de cola”. Se obtiene de la columna “Saliente”."
    )
    #movil_prioritarios: int = Field(
    #    description="Total de llamadas salientes respecto a MOVIL_Prioritarios. Se obtiene de la columna “Saliente”."
    #)
    salientes_movil: int = Field(
        description="Total de llamadas salientes respecto al valor Salientes_Movil en la columna “Nombre de cola”. Se obtiene de la columna “Saliente”."
    )

    @property
    def total(self):
        return (
            self.movil_contratos
            + self.movil_prepagos
            #+ self.movil_prioritarios
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
    antel_movil_global: AntelMovilGlobal
    antel_movil_no_global: AntelMovilNoGlobal
    incidencias: Incidencias
    reclamos: Reclamos
    motivosIzi611: MotivosIZI611
    motivos_contacto: MotivosContacto
    whatsapp: Whatsapp
    salientes: Salientes
    automatismos: Automatismos
    lista_dias: Optional[list[int]]
    mes: Optional[int]
    anio: Optional[int]


if __name__ == "__main__":
    print(Reporte.model_json_schema())
