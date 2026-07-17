# Documentacion no tecnica de FaultMate

## 1. Que es FaultMate
FaultMate es una plataforma web para ayudar en el diagnostico de fallas industriales.
El objetivo es que el equipo tecnico pueda registrar fallas, obtener sugerencias de causa raiz y documentar acciones correctivas de forma simple.

## 2. Como funciona en palabras sencillas
1. El usuario inicia sesion con su cuenta.
2. Puede escribir una falla en el modulo Diagnosticar.
3. El sistema busca primero informacion conocida en la base de datos.
4. Si no hay una coincidencia directa, se apoya en IA para generar una orientacion inicial.
5. Todo queda guardado en historial para consulta posterior.

## 3. Flujo de diagnostico
### Diagnostico directo
- Se ingresa una falla.
- Si existe un registro compatible, se muestra el diagnostico guardado.
- El usuario puede abrir el detalle completo.
- Desde el historial, el usuario puede eliminar registros no deseados.

### Diagnostico con arbol de decision (si/no)
- En chats de agentes, si el mensaje coincide con una falla conocida, se activa un arbol de decision.
- El sistema hace preguntas cortas y espera respuesta "si" o "no".
- Al finalizar las preguntas, muestra posibles causas raiz y acciones correctivas.
- Si la falla no existe en el arbol, el sistema usa IA como respaldo.

## 4. Como se crean y usan los agentes
- Hay agentes base (precargados) y agentes personalizados.
- Los perfiles con permisos de gestion pueden:
  - crear agentes manualmente,
  - generar agentes con configuracion sugerida,
  - editar o eliminar agentes.
- Cualquier usuario con acceso puede abrir chat con un agente y guardar la conversacion.

## 5. Gestion de usuarios
- Existe un modulo para alta, edicion y eliminacion de usuarios.
- El alta de usuarios se hace desde una pantalla dedicada (Crear usuario).
- Solo los roles autorizados pueden crear o modificar usuarios.

## 6. Como se conecta la informacion (base de datos)
FaultMate trabaja con una base de datos para guardar:
- usuarios,
- diagnosticos,
- agentes,
- conversaciones,
- preguntas y causas raiz.

En ambientes de desarrollo puede usar una base local.
En ambientes productivos puede conectarse a una base administrada en la nube.

## 7. Que gana el equipo con este flujo
- Menos tiempo buscando causas repetidas.
- Diagnosticos mas uniformes entre turnos y personas.
- Historial centralizado para auditoria y mejora continua.
- Escalabilidad: se pueden agregar mas fallas, preguntas y agentes con el tiempo.

## 8. Recomendaciones operativas
- Mantener actualizado el catalogo de fallas, preguntas y causas raiz.
- Revisar periodicamente los diagnosticos generados por IA.
- Eliminar del historial registros erroneos para mantener calidad de datos.
- Definir claramente que roles pueden crear usuarios o agentes.
