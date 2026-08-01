# Backups básicos de PostgreSQL

## Objetivo y alcance

Este runbook protege la base PostgreSQL del despliegue Compose. No incluye los objetos S3/MinIO;
estos requieren un backup coordinado independiente. Un dump no se considera válido hasta completar
una restauración de prueba.

## Política mínima

- Ejecutar un backup diario y antes de migraciones o despliegues con cambios de datos.
- Conservar al menos 7 copias diarias y 4 semanales, salvo que la política legal aprobada exija otro plazo.
- Cifrar cada copia antes de sacarla del host y almacenarla en una ubicación separada con acceso restringido.
- No guardar dumps en Git, imágenes Docker, logs ni volúmenes efímeros del contenedor.
- Registrar fecha UTC, ambiente, revisión Alembic, tamaño, checksum SHA-256, ubicación y resultado del restore drill.
- Los datos eliminados mediante `SEC-003` pueden permanecer en backups hasta expirar su retención;
  una solicitud de borrado debe registrar esa limitación y evitar restauraciones no controladas.

## Crear un backup

Desde la raíz del repositorio, con el perfil productivo levantado:

```powershell
$backupStamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$backupDir = Join-Path (Get-Location) "backups"
$backupFile = Join-Path $backupDir "abogado-facil-$backupStamp.dump"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
docker compose -f compose.yaml -f compose.prod.yaml exec -T database sh -c 'umask 077; pg_dump --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --format=custom --compress=9 --no-owner --no-privileges --file=/tmp/abogado-facil.dump'
docker compose -f compose.yaml -f compose.prod.yaml cp database:/tmp/abogado-facil.dump $backupFile
docker compose -f compose.yaml -f compose.prod.yaml exec -T database rm -f /tmp/abogado-facil.dump
Get-FileHash -Algorithm SHA256 -LiteralPath $backupFile
```

Comprueba que el archivo existe, no está vacío y su hash quedó registrado. Cífralo con el mecanismo
aprobado por el operador antes de transferirlo. La clave de cifrado debe administrarse fuera del host
y fuera del repositorio.

## Verificar y restaurar en aislamiento

Nunca pruebes una restauración sobre la base productiva. Copia el dump a un contenedor PostgreSQL
aislado o usa un nombre temporal sin conexiones de aplicación:

```powershell
$restoreDb = "abogado_facil_restore_test"
docker compose -f compose.yaml -f compose.prod.yaml cp $backupFile database:/tmp/abogado-facil.dump
docker compose -f compose.yaml -f compose.prod.yaml exec -T --env RESTORE_DB=$restoreDb database sh -c 'dropdb --username="$POSTGRES_USER" --if-exists "$RESTORE_DB"; createdb --username="$POSTGRES_USER" "$RESTORE_DB"; pg_restore --username="$POSTGRES_USER" --dbname="$RESTORE_DB" --exit-on-error --no-owner --no-privileges /tmp/abogado-facil.dump'
docker compose -f compose.yaml -f compose.prod.yaml exec -T --env RESTORE_DB=$restoreDb database sh -c 'psql --username="$POSTGRES_USER" --dbname="$RESTORE_DB" --tuples-only --command="SELECT count(*) FROM alembic_version;"'
docker compose -f compose.yaml -f compose.prod.yaml exec -T --env RESTORE_DB=$restoreDb database sh -c 'dropdb --username="$POSTGRES_USER" --if-exists "$RESTORE_DB"; rm -f /tmp/abogado-facil.dump'
```

La prueba pasa solo si `pg_restore` termina sin error, existe una revisión Alembic y las comprobaciones
funcionales definidas por el operador son coherentes. Registra el resultado y elimina la base temporal.

## Fallos y recuperación

- Si `pg_dump`, copia, checksum o cifrado falla, elimina el artefacto incompleto y vuelve a ejecutar.
- Si el restore drill falla, conserva el dump cifrado para investigación, genera uno nuevo y no lo marques válido.
- Antes de una restauración real, detén escritores, crea un backup de emergencia y documenta quién la autorizó.
- Tras restaurar, ejecuta migraciones, readiness y smoke tests antes de reabrir tráfico.

## Checklist de evidencia

- [ ] Dump custom completado sin error.
- [ ] Archivo fuera del contenedor, cifrado y con acceso restringido.
- [ ] SHA-256 y tamaño registrados.
- [ ] Copia externa confirmada.
- [ ] Restore drill aislado aprobado.
- [ ] Artefactos y base temporal eliminados.
- [ ] Retención y próxima fecha de prueba registradas.
