# Capa BRONCE (SQL)
Copia cruda de los CSV de Transfermarkt: todas las columnas son TEXT y no se corrige nada.
Cada tabla añade `_load_id`, `_loaded_at`, `_source_file` y `_row_id` para linaje.
Se trunca y se recarga en cada ejecución (idempotente).
