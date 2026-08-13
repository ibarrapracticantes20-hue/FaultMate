# Comando de administracion: carga las 10 fallas manuales del arbol de
# decision (checklist de tecnico) con sus preguntas ramificadas y sus
# causas raiz + accion correctiva + recomendacion de seguridad (LOTO).
#
# Se ejecuta UNA vez con:
#   python manage.py cargar_fallas_manuales
#
# Es seguro correrlo varias veces: si una falla ya existe (por nombre),
# se salta y no duplica nada.
from django.core.management.base import BaseCommand
from agentes.models import Falla, PreguntaDiagnostico, CausaRaiz

LOTO_ESTANDAR = (
    'Aplica bloqueo y etiquetado (LOTO) antes de intervenir el equipo: '
    'desenergiza y bloquea la fuente de energía, y libera presión '
    'residual hidráulica/neumática si aplica.'
)


def causa(causa_texto, accion_texto, con_loto=True):
    return {
        'causa': causa_texto,
        'accion': accion_texto,
        'loto': LOTO_ESTANDAR if con_loto else '',
    }


ARBOLES = [
    {
        'nombre': 'Motor no arranca',
        'descripcion': 'Diagnóstico guiado cuando el motor no arranca.',
        'arbol': {
            'pregunta': '¿Hay voltaje en los bornes del motor?',
            'no': {'causas': [causa(
                'Falla en suministro de energía / Fusible abierto / Contactor sin accionamiento / Cable suelto',
                'Revisar fusibles; Revisar breaker; Medir voltajes L1-L2-L3',
            )]},
            'si': {
                'pregunta': '¿El contactor está activo?',
                'no': {'causas': [causa(
                    'Contactor dañado / Bobina quemada / Falta señal de control / Pulsador está descompuesto',
                    'Revisar bobina; Revisar control 24V/120V',
                )]},
                'si': {
                    'pregunta': '¿El motor hace zumbido?',
                    'si': {'causas': [causa(
                        'Sobrecarga mecánica / Corriente elevada / Desgaste en rodamientos / Rotor bloqueado o eje atascado',
                        'Revisar amperaje; Verificar libre giro del eje; Inspeccionar rodamientos',
                    )]},
                    'no': {'causas': [causa(
                        'Posible falla en el devanado del motor',
                        'Revisar continuidad del devanado',
                    )]},
                },
            },
        },
    },
    {
        'nombre': 'Baja presión hidráulica',
        'descripcion': 'Diagnóstico guiado para baja presión en sistema hidráulico.',
        'arbol': {
            'pregunta': '¿La máquina se mueve mucho más lento de lo normal o le cuesta arrancar?',
            'si': {'causas': [causa(
                'Aceite viejo / Entrada de aire en las mangueras (burbujas) / Falta de fuerza en la bomba / Filtro de aceite tapado',
                'Limpiar los filtros de aceite; Verificar el estado de la bomba; Ajustar conexiones',
            )]},
            'no': {
                'pregunta': '¿Existen fugas visibles de aceite?',
                'si': {'causas': [causa(
                    'Mangueras rotas / Tuercas flojas / Sellos desgastados / Golpe en el tanque de almacenamiento',
                    'Cambiar manguera; Reemplazar sellos; Reparar la grieta del tanque',
                )]},
                'no': {
                    'pregunta': '¿La válvula de alivio está dañada?',
                    'no': {'causas': [causa(
                        'Válvula atascada / Resorte dañado / Aceite contaminado por agua / Filtro hidráulico obstruido',
                        'Limpiar válvula; Reemplazar el resorte; Cambiar el filtro de aceite',
                    )]},
                    'si': {'causas': [causa(
                        'Posible descalibración de presión del sistema',
                        'Verificar calibración de presión',
                        con_loto=False,
                    )]},
                },
            },
        },
    },
    {
        'nombre': 'Movimiento lento',
        'descripcion': 'Diagnóstico guiado cuando el equipo se mueve más lento de lo normal.',
        'arbol': {
            'pregunta': '¿El nivel de lubricación es bajo?',
            'si': {'causas': [causa(
                'Lubricación insuficiente / Bajo nivel de aceite / Componentes secos o desgastados / Fugas de aceite',
                'Rellenar aceite; Lubricar componentes; Revisar fugas',
            )]},
            'no': {
                'pregunta': '¿La bomba o motor hace ruido anormal?',
                'si': {'causas': [causa(
                    'Bomba desgastada / Rodamientos dañados / Aire en el sistema / Filtro tapado',
                    'Revisar bomba; Revisar rodamientos; Ajustar piezas flojas',
                )]},
                'no': {
                    'pregunta': '¿Hay piezas atoradas o suciedad?',
                    'no': {'causas': [causa(
                        'Obstrucción mecánica / Acumulación de residuos / Sistema de lubricación deficiente / Suciedad en el sistema',
                        'Limpiar el sistema; Retirar obstrucciones mecánicas; Agregar lubricación',
                    )]},
                    'si': {'causas': [causa(
                        'Posible falla en el suministro eléctrico del equipo',
                        'Revisar la energía eléctrica',
                    )]},
                },
            },
        },
    },
    {
        'nombre': 'Fuga de aceite',
        'descripcion': 'Diagnóstico guiado ante fuga de aceite visible.',
        'arbol': {
            'pregunta': '¿Se observa aceite tirado o goteando?',
            'no': {'causas': [causa(
                'Manguera dañada / Conexión floja / Sello desgastado / Tubo roto',
                'Cambiar manguera; Ajustar conexiones; Revisar tuberías',
            )]},
            'si': {
                'pregunta': '¿El nivel de aceite baja rápidamente?',
                'si': {'causas': [causa(
                    'Fuga interna / Sello dañado / Depósito con fuga / Exceso de presión',
                    'Revisar sellos; Revisar tanque; Verificar presión',
                )]},
                'no': {
                    'pregunta': '¿Hay olor fuerte o manchas cerca del sistema?',
                    'si': {'causas': [causa(
                        'Aceite derramado / Empaque dañado / Conexión mal ajustada / Acumulación de residuos',
                        'Limpiar área; Ajustar conexiones; Cambiar empaques',
                    )]},
                    'no': {'causas': [causa(
                        'Posible descalibración de presión del sistema',
                        'Revisar presión del sistema',
                        con_loto=False,
                    )]},
                },
            },
        },
    },
    {
        'nombre': 'Sobrecalentamiento de motor',
        'descripcion': 'Diagnóstico guiado ante sobrecalentamiento del motor.',
        'arbol': {
            'pregunta': '¿El motor tiene muy poca ventilación?',
            'si': {'causas': [causa(
                'Ventilador sucio / Entradas de aire tapadas / Exceso de polvo / Mala ventilación',
                'Limpiar ventilación; Destapar ventilación; Limpiar polvo',
            )]},
            'no': {
                'pregunta': '¿El motor hace ruido o vibración?',
                'si': {'causas': [causa(
                    'Rodamientos dañados / Partes desgastadas / Aire atorado / Desajuste en transmisión',
                    'Revisar rodamientos; Lubricar piezas; Ajustar componentes',
                )]},
                'no': {
                    'pregunta': '¿El motor trabaja con mucha carga?',
                    'no': {'causas': [causa(
                        'Sobrecarga / Corriente elevada / Voltaje incorrecto / Uso continuo excesivo',
                        'Revisar amperaje; Verificar voltaje; Reducir carga',
                    )]},
                    'si': {'causas': [causa(
                        'Posible consumo eléctrico fuera de rango',
                        'Verificar consumo eléctrico',
                        con_loto=False,
                    )]},
                },
            },
        },
    },
    {
        'nombre': 'Vibración excesiva',
        'descripcion': 'Diagnóstico guiado ante vibración excesiva del equipo.',
        'arbol': {
            'pregunta': '¿Hay tornillos o piezas flojas?',
            'si': {'causas': [causa(
                'Tornillos flojos / Piezas mal ajustadas / Base inestable / Componentes sueltos',
                'Ajustar tornillos; Revisar soportes; Verificar base del equipo',
            )]},
            'no': {
                'pregunta': '¿El motor hace ruido anormal?',
                'no': {'causas': [causa(
                    'Rodamientos dañados / Partes desgastadas / Problema de alineación / Falta de lubricación',
                    'Revisar rodamientos; Lubricar componentes; Ajustar alineación',
                )]},
                'si': {
                    'pregunta': '¿La máquina trabaja con mucho peso o carga?',
                    'si': {'causas': [causa(
                        'Desbalance / Acumulación de suciedad / Mala distribución de carga / Exceso de trabajo',
                        'Reducir carga; Balancear sistema; Verificar capacidad del equipo',
                    )]},
                    'no': {'causas': [causa(
                        'Posible falla intermitente por ruido/movimiento no identificado',
                        'Verificar monitoreo de ruidos y movimiento',
                        con_loto=False,
                    )]},
                },
            },
        },
    },
    {
        'nombre': 'Banda detenida',
        'descripcion': 'Diagnóstico guiado cuando la banda transportadora se detiene.',
        'arbol': {
            'pregunta': '¿La banda tiene objetos atorados?',
            'si': {'causas': [causa(
                'Obstrucción / Material atorado / Exceso de carga / Rodillos bloqueados',
                'Retirar obstrucciones; Limpiar banda; Revisar rodillos',
            )]},
            'no': {
                'pregunta': '¿El motor de la banda enciende?',
                'si': {'causas': [causa(
                    'Banda floja / Polea dañada / Deslizamiento mal ajustado / Falta de tensión',
                    'Ajustar banda; Revisar poleas; Verificar tensión',
                )]},
                'no': {
                    'pregunta': '¿Hay energía eléctrica en el sistema?',
                    'si': {'causas': [causa(
                        'Contactor dañado / Fusible abierto / Cable flojo / Protección activada',
                        'Revisar contactor; Revisar fusibles; Ajustar cableado',
                    )]},
                    'no': {'causas': [causa(
                        'Posible falla en el tablero de control',
                        'Revisar tablero de control',
                    )]},
                },
            },
        },
    },
    {
        'nombre': 'Cilindro no avanza',
        'descripcion': 'Diagnóstico guiado cuando el cilindro no avanza.',
        'arbol': {
            'pregunta': '¿Hay presión de aire o aceite en el sistema?',
            'si': {'causas': [causa(
                'Válvula dañada / Manguera doblada / Fuga en el sistema / Aire atrapado',
                'Revisar válvula; Revisar mangueras; Reparar fugas',
            )]},
            'no': {
                'pregunta': '¿El cilindro hace ruido o intenta moverse?',
                'si': {'causas': [causa(
                    'Pistón atorado / Suciedad interna / Poca lubricación / Partes desgastadas',
                    'Limpiar cilindro; Lubricar componentes; Revisar desgastes',
                )]},
                'no': {
                    'pregunta': '¿La válvula de control activa correctamente?',
                    'si': {'causas': [causa(
                        'Baja presión / Conexión floja / Filtro tapado / Flujo insuficiente',
                        'Revisar presión; Limpiar filtro; Revisar flujo',
                    )]},
                    'no': {'causas': [causa(
                        'Posible falla mecánica no identificada en el cilindro',
                        'Confirmar funcionamiento del cilindro',
                        con_loto=False,
                    )]},
                },
            },
        },
    },
    {
        'nombre': 'Bomba sin presión',
        'descripcion': 'Diagnóstico guiado cuando la bomba no genera presión.',
        'arbol': {
            'pregunta': '¿La bomba tiene suficiente aceite o fluido?',
            'no': {'causas': [causa(
                'Falta de aceite / Fuga de fluido / Nivel bajo / Sistema vacío',
                'Agregar aceite; Revisar fugas; Revisar depósito; Llenar sistema',
            )]},
            'si': {
                'pregunta': '¿Se escuchan ruidos extraños en la bomba?',
                'si': {'causas': [causa(
                    'Aire en el sistema / Bomba desgastada / Filtro tapado / Partes dañadas',
                    'Purgar sistema; Revisar bomba; Revisar piezas dañadas',
                )]},
                'no': {
                    'pregunta': '¿La presión sube muy lento?',
                    'si': {'causas': [causa(
                        'Baja presión / Manguera floja / Válvula dañada / Fuga interna',
                        'Revisar presión; Revisar válvula; Revisar fugas',
                    )]},
                    'no': {'causas': [causa(
                        'Posible descalibración de presión del sistema',
                        'Revisar que la presión sea normal',
                        con_loto=False,
                    )]},
                },
            },
        },
    },
    {
        'nombre': 'Ruido en motor',
        'descripcion': 'Diagnóstico guiado ante ruido anormal en el motor.',
        'arbol': {
            'pregunta': '¿El motor presenta un zumbido anormal?',
            'si': {'causas': [causa(
                'Falta de voltaje / Contactor dañado / Capacitor dañado / Sobrecarga',
                'Revisar capacitor; Revisar contactor; Revisar carga del motor',
            )]},
            'no': {
                'pregunta': '¿Se escuchan golpes o vibración?',
                'si': {'causas': [causa(
                    'Sobrecarga / Mala ventilación / Exceso de trabajo / Suciedad acumulada',
                    'Limpiar ventilación; Reducir carga; Dejar enfriar motor; Limpiar suciedad',
                )]},
                'no': {
                    'pregunta': '¿El motor se calienta demasiado?',
                    'si': {'causas': [causa(
                        'Rodamientos dañados / Piezas flojas / Componentes fuera de posición / Falta de lubricación',
                        'Revisar rodamientos; Ajustar piezas; Revisar alineación; Agregar lubricación',
                    )]},
                    'no': {'causas': [causa(
                        'Posible falla intermitente por temperatura/vibración no identificada',
                        'Monitorear temperatura y vibración',
                        con_loto=False,
                    )]},
                },
            },
        },
    },
]


class Command(BaseCommand):
    help = 'Carga las 10 fallas manuales del arbol de decision con sus preguntas y causas raiz.'

    def handle(self, *args, **options):
        for item in ARBOLES:
            if Falla.objects.filter(nombre=item['nombre']).exists():
                self.stdout.write(self.style.WARNING(f'Ya existe: {item["nombre"]} (se omite)'))
                continue

            falla = Falla.objects.create(nombre=item['nombre'], descripcion=item['descripcion'])
            self._crear_nodo(falla, item['arbol'], pregunta_padre=None, respuesta_padre=None, orden=[0])
            self.stdout.write(self.style.SUCCESS(f'Cargada: {item["nombre"]}'))

        self.stdout.write(self.style.SUCCESS('Listo.'))

    def _crear_nodo(self, falla, nodo, pregunta_padre, respuesta_padre, orden):
        if 'pregunta' in nodo:
            orden[0] += 1
            pregunta = PreguntaDiagnostico.objects.create(
                falla=falla,
                pregunta=nodo['pregunta'],
                orden=orden[0],
                pregunta_padre=pregunta_padre,
                respuesta_padre=respuesta_padre,
            )
            self._crear_nodo(falla, nodo['si'], pregunta, 'si', orden)
            self._crear_nodo(falla, nodo['no'], pregunta, 'no', orden)
        else:
            for c in nodo.get('causas', []):
                CausaRaiz.objects.create(
                    falla=falla,
                    pregunta_disparadora=pregunta_padre,
                    respuesta_disparadora=respuesta_padre,
                    causa=c['causa'],
                    accion_correctiva=c['accion'],
                    recomendacion_seguridad=c['loto'],
                )
